import Mathlib

/-!
# Characteristic-two / GF(2) identities
These universal theorems do not yet certify the concrete Golay 23x11 matrix
rank, quantum code distance, or any physical QEC realization.
-/

namespace Edgewalk.GF2

abbrev Bit := ZMod 2

def dot {n : Nat} (u v : Fin n → Bit) : Bit :=
  ∑ i, u i * v i

theorem self_add_zero (x : Bit) : x + x = 0 := by
  have htwo : (2 : Bit) = 0 := by decide
  calc
    x + x = (2 : Bit) * x := by ring
    _ = 0 := by rw [htwo]; simp

theorem xor_cancel (x y : Bit) : x + y + x = y := by
  calc
    x + y + x = (x + x) + y := by abel
    _ = y := by rw [self_add_zero]; simp

theorem dot_symmetric {n : Nat} (u v : Fin n → Bit) :
    dot u v = dot v u := by
  unfold dot
  apply Finset.sum_congr rfl
  intro i _
  exact mul_comm (u i) (v i)

theorem dot_add_left {n : Nat} (u v w : Fin n → Bit) :
    dot (fun i => u i + v i) w = dot u w + dot v w := by
  unfold dot
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem dot_duplicate_zero {n : Nat} (u v : Fin n → Bit) :
    dot u (fun i => v i + v i) = 0 := by
  simp [dot, self_add_zero]

end Edgewalk.GF2
