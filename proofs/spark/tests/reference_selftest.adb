with Ada.Text_IO;
with Edgewalk_Reference;

procedure Reference_Selftest is
   use Edgewalk_Reference;
   Graph : Adjacency := (others => (others => False));
   Target : Vertex;
   Accepted : Boolean;
begin
   for N in Sequence_Index loop
      declare
         A : constant Address := Address_Of (N);
      begin
         if Sequence_Of (A.Site, A.Fibre) /= N
           or else A.Tensor /= Tensor_Of (A.Site, A.Fibre)
           or else A.Phase /= Phase_Of (A.Fibre)
         then
            raise Program_Error with "CRT/phase mismatch";
         end if;
      end;
   end loop;

   for S in Site_Index loop
      for F in Fibre_Index loop
         declare
            N : constant Sequence_Index := Sequence_Of (S, F);
            A : constant Address := Address_Of (N);
         begin
            if A.Site /= S or else A.Fibre /= F then
               raise Program_Error with "inverse CRT mismatch";
            end if;
         end;
      end loop;
   end loop;

   if Parity (0, Word_23'Last) /= 0
     or else Parity (Word_23'Last, Word_23'Last) /= 1
     or else Parity (3, 3) /= 0
     or else Parity (5, 1) /= 1
   then
      raise Program_Error with "GF2 parity mismatch";
   end if;

   Graph (0, 23) := True;
   Graph (23, 0) := True;
   Checked_Step (Graph, 0, 23, Target, Accepted);
   if not Accepted or else Target /= 23 then
      raise Program_Error with "valid edge rejected";
   end if;
   Checked_Step (Graph, 0, 24, Target, Accepted);
   if Accepted or else Target /= 0 then
      raise Program_Error with "nonedge accepted";
   end if;
   Checked_Step (Graph, 0, 0, Target, Accepted);
   if Accepted or else Target /= 0 then
      raise Program_Error with "self-loop accepted";
   end if;
   Graph (23, 0) := False;
   Checked_Step (Graph, 0, 23, Target, Accepted);
   if Accepted or else Target /= 0 then
      raise Program_Error with "one-way edge accepted";
   end if;
   Ada.Text_IO.Put_Line ("ADA_REFERENCE_SELFTEST=PASS (runtime tests only)");
end Reference_Selftest;
