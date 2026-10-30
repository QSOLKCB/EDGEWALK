import Edgewalk.CRT

/-!
# Gaussian unit phase exponents
The modulo-4 phase exponents (3,2,3) correspond to (-i,-1,-i).
-/

namespace Edgewalk.Phase

def nextFibre (a : Fin 3) : Fin 3 :=
  ⟨(a.val + 1) % 3, Nat.mod_lt _ (by omega)⟩

def exponent (a : Fin 3) : ZMod 4 :=
  if a.val = 1 then 2 else 3

def potential (a : Fin 3) : ZMod 4 :=
  if a.val = 0 then 0 else if a.val = 1 then 3 else 1

theorem exponent_is_potential_difference (a : Fin 3) :
    exponent a = potential (nextFibre a) - potential a := by
  fin_cases a <;> decide

theorem three_step_closure (a : Fin 3) :
    exponent a + exponent (nextFibre a) +
      exponent (nextFibre (nextFibre a)) = 0 := by
  fin_cases a <;> decide

theorem aligned_phase_exponents :
    exponent (0 : Fin 3) = 3 ∧
    exponent (1 : Fin 3) = 2 ∧
    exponent (2 : Fin 3) = 3 := by
  decide

theorem total_phase_after_101_fibre_cycles :
    (101 : ZMod 4) *
      (exponent (0 : Fin 3) + exponent (1 : Fin 3) +
        exponent (2 : Fin 3)) = 0 := by
  have h : exponent (0 : Fin 3) + exponent (1 : Fin 3) +
      exponent (2 : Fin 3) = 0 := by decide
  rw [h]
  simp

end Edgewalk.Phase
