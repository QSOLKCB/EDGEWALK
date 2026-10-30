--  Reference-only arithmetic contracts. No QEC/ETQ source identity is asserted.
--  SPARK_Mode On covers declarations AND the corresponding package body.
package Edgewalk_Reference with SPARK_Mode => On is
   type Sequence_Index is range 0 .. 302;
   type Site_Index is range 0 .. 100;
   type Fibre_Index is range 0 .. 2;
   type Tensor_Index is range 0 .. 302;
   type Phase_Exponent is range 2 .. 3;
   type Bit is range 0 .. 1;
   type Word_23 is mod 2 ** 23;

   type Address is record
      Site   : Site_Index;
      Fibre  : Fibre_Index;
      Tensor : Tensor_Index;
      Phase  : Phase_Exponent;
   end record;

   function Tensor_Of (Site : Site_Index; Fibre : Fibre_Index)
      return Tensor_Index
   with Global => null,
        Post => Tensor_Of'Result =
          Tensor_Index (3 * Integer (Site) + Integer (Fibre));

   function Phase_Of (Fibre : Fibre_Index) return Phase_Exponent
   with Global => null,
        Post => (if Fibre = 1 then Phase_Of'Result = 2
                 else Phase_Of'Result = 3);

   function Address_Of (N : Sequence_Index) return Address
   with Global => null,
        Post =>
          Address_Of'Result.Site = Site_Index (Integer (N) mod 101)
          and then Address_Of'Result.Fibre =
            Fibre_Index (Integer (N) mod 3)
          and then Address_Of'Result.Tensor =
            Tensor_Index (3 * (Integer (N) mod 101) + Integer (N) mod 3)
          and then Address_Of'Result.Phase =
            (if Integer (N) mod 3 = 1 then 2 else 3);

   function Sequence_Of (Site : Site_Index; Fibre : Fibre_Index)
      return Sequence_Index
   with Global => null,
        Post =>
          Integer (Sequence_Of'Result) mod 101 = Integer (Site)
          and then Integer (Sequence_Of'Result) mod 3 = Integer (Fibre);

   function Parity (A, B : Word_23) return Bit
   with Global => null,
        Post => (if A = 0 or else B = 0 then Parity'Result = 0);

   type Vertex is range 0 .. 44;
   type Adjacency is array (Vertex, Vertex) of Boolean;

   function Is_Valid_Edge
     (Graph : Adjacency; Source, Candidate : Vertex) return Boolean
   with Global => null,
        Post => Is_Valid_Edge'Result =
          (Source /= Candidate
            and then Graph (Source, Candidate)
            and then Graph (Candidate, Source));

   procedure Checked_Step
     (Graph : in Adjacency;
      Source, Candidate : in Vertex;
      Target : out Vertex;
      Accepted : out Boolean)
   with Global => null,
        Depends => (Target => (Graph, Source, Candidate),
                    Accepted => (Graph, Source, Candidate)),
        Post =>
          Accepted = Is_Valid_Edge (Graph, Source, Candidate)
          and then (if Accepted then Target = Candidate else Target = Source);

end Edgewalk_Reference;
