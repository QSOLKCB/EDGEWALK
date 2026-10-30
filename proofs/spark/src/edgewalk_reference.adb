package body Edgewalk_Reference with SPARK_Mode => On is

   function Tensor_Of (Site : Site_Index; Fibre : Fibre_Index)
      return Tensor_Index
   is
   begin
      return Tensor_Index (3 * Integer (Site) + Integer (Fibre));
   end Tensor_Of;

   function Phase_Of (Fibre : Fibre_Index) return Phase_Exponent is
   begin
      if Fibre = 1 then
         return 2;
      else
         return 3;
      end if;
   end Phase_Of;

   function Address_Of (N : Sequence_Index) return Address is
      S : constant Site_Index := Site_Index (Integer (N) mod 101);
      F : constant Fibre_Index := Fibre_Index (Integer (N) mod 3);
   begin
      return (Site   => S,
              Fibre  => F,
              Tensor => Tensor_Of (S, F),
              Phase  => Phase_Of (F));
   end Address_Of;

   function Sequence_Of (Site : Site_Index; Fibre : Fibre_Index)
      return Sequence_Index
   is
      --  101 = 2 (mod 3), hence 2 is its own inverse mod 3.
      Offset : constant Integer :=
        (2 * (Integer (Fibre) + 3 - Integer (Site) mod 3)) mod 3;
   begin
      return Sequence_Index (Integer (Site) + 101 * Offset);
   end Sequence_Of;

   function Parity (A, B : Word_23) return Bit is
      Remaining : Word_23 := A and B;
      Result_Bit : Bit := 0;
   begin
      --  Bounded 23-iteration shift over exactly the 23 supported bits.
      for I in 1 .. 23 loop
         if Remaining mod 2 = 1 then
            Result_Bit := 1 - Result_Bit;
         end if;
         Remaining := Remaining / 2;
         pragma Loop_Invariant (Result_Bit in Bit);
         pragma Loop_Invariant (Remaining <= Word_23'Last);
      end loop;
      return Result_Bit;
   end Parity;

   function Is_Valid_Edge
     (Graph : Adjacency; Source, Candidate : Vertex) return Boolean
   is
   begin
      return Source /= Candidate
        and then Graph (Source, Candidate)
        and then Graph (Candidate, Source);
   end Is_Valid_Edge;

   procedure Checked_Step
     (Graph : in Adjacency;
      Source, Candidate : in Vertex;
      Target : out Vertex;
      Accepted : out Boolean)
   is
   begin
      Accepted := Is_Valid_Edge (Graph, Source, Candidate);
      if Accepted then
         Target := Candidate;
      else
         Target := Source;
      end if;
   end Checked_Step;

end Edgewalk_Reference;
