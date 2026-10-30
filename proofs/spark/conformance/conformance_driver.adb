--  v0.7.2 differential test driver. This IO harness is NOT SPARK-proved.
--  Only calls the unchanged separately audited Edgewalk_Reference package.
with Ada.Text_IO;
with Ada.Strings;
with Ada.Strings.Fixed;
with Edgewalk_Reference;

procedure Conformance_Driver is
   use Ada.Text_IO;
   use Edgewalk_Reference;

   function Decimal (N : Integer) return String is
     (Ada.Strings.Fixed.Trim (Integer'Image (N), Ada.Strings.Both));

   procedure Read_Number
     (Line : String; Position : in out Natural; Value : out Integer)
   is
      Acc : Natural := 0;
      Digit : Natural;
      Seen : Boolean := False;
   begin
      if Position > Line'Last then
         raise Constraint_Error with "missing integer token";
      end if;
      while Position <= Line'Last and then Line (Position) /= ' ' loop
         if Line (Position) not in '0' .. '9' then
            raise Constraint_Error with "non-decimal integer token";
         end if;
         Digit := Character'Pos (Line (Position)) - Character'Pos ('0');
         if Acc > (8_388_607 - Digit) / 10 then
            raise Constraint_Error with "integer exceeds 23-bit bound";
         end if;
         Acc := Acc * 10 + Digit;
         Position := Position + 1;
         Seen := True;
      end loop;
      if not Seen then
         raise Constraint_Error with "empty integer token";
      end if;
      Value := Integer (Acc);
      if Position <= Line'Last then
         Position := Position + 1;
         if Position > Line'Last or else Line (Position) = ' ' then
            raise Constraint_Error with "trailing or doubled whitespace";
         end if;
      end if;
   end Read_Number;

   function Flag (Value : Integer) return Boolean is
   begin
      if Value > 1 then
         raise Constraint_Error with "edge flag must be 0 or 1";
      end if;
      return Value = 1;
   end Flag;

   function Bool_Digit (Value : Boolean) return String is
     (if Value then "1" else "0");

   Line_Count : Natural := 0;
begin
   while not End_Of_File (Standard_Input) loop
      declare
         Line : constant String := Get_Line (Standard_Input);
         Pos : Natural := Line'First + 2;
         A, B, C, D : Integer := 0;
      begin
         Line_Count := Line_Count + 1;
         if Line'Length < 3 or else Line (Line'First + 1) /= ' ' then
            raise Constraint_Error with "invalid conformance record prefix";
         end if;
         case Line (Line'First) is
            when 'A' =>
               Read_Number (Line, Pos, A);
               if Pos <= Line'Last or else A > 302 then
                  raise Constraint_Error with "invalid address record";
               end if;
               declare
                  Addr : constant Address := Address_Of (Sequence_Index (A));
               begin
                  Put_Line ("A " & Decimal (A) & " " &
                    Decimal (Integer (Addr.Site)) & " " &
                    Decimal (Integer (Addr.Fibre)) & " " &
                    Decimal (Integer (Addr.Tensor)) & " " &
                    Decimal (Integer (Addr.Phase)));
               end;
            when 'I' =>
               Read_Number (Line, Pos, A);
               Read_Number (Line, Pos, B);
               if Pos <= Line'Last or else A > 100 or else B > 2 then
                  raise Constraint_Error with "invalid inverse record";
               end if;
               Put_Line ("I " & Decimal (A) & " " & Decimal (B) & " " &
                 Decimal (Integer (Sequence_Of (Site_Index (A),
                                               Fibre_Index (B)))));
            when 'P' =>
               Read_Number (Line, Pos, A);
               Read_Number (Line, Pos, B);
               if Pos <= Line'Last then
                  raise Constraint_Error with "invalid parity record";
               end if;
               Put_Line ("P " & Decimal (A) & " " & Decimal (B) & " " &
                 Decimal (Integer (Parity (Word_23 (A), Word_23 (B)))));
            when 'E' =>
               Read_Number (Line, Pos, A);
               Read_Number (Line, Pos, B);
               Read_Number (Line, Pos, C);
               Read_Number (Line, Pos, D);
               if Pos <= Line'Last or else A > 44 or else B > 44 then
                  raise Constraint_Error with "invalid edge record";
               end if;
               declare
                  Graph : Adjacency := (others => (others => False));
                  Target : Vertex;
                  Accepted : Boolean;
               begin
                  Graph (Vertex (A), Vertex (B)) := Flag (C);
                  Graph (Vertex (B), Vertex (A)) := Flag (D);
                  Checked_Step (Graph, Vertex (A), Vertex (B),
                                Target, Accepted);
                  Put_Line ("E " & Decimal (A) & " " & Decimal (B) & " " &
                    Decimal (C) & " " & Decimal (D) & " " &
                    Bool_Digit (Accepted) & " " &
                    Decimal (Integer (Target)));
               end;
            when others =>
               raise Constraint_Error with "unknown conformance opcode";
         end case;
      end;
   end loop;
   if Line_Count = 0 then
      raise Constraint_Error with "empty conformance input";
   end if;
end Conformance_Driver;
