import Mathlib

/-!
# ETQ-303 exact CRT addressing
Addresses are protocol coordinates, not physical spacetime dimensions.
-/

namespace Edgewalk.CRT

def address (n : Fin 303) : Fin 101 × Fin 3 :=
  (⟨n.val % 101, Nat.mod_lt _ (by omega)⟩,
   ⟨n.val % 3, Nat.mod_lt _ (by omega)⟩)

def inverse (p : Fin 101 × Fin 3) : Fin 303 :=
  ⟨p.1.val + 101 * ((2 * (p.2.val + 3 - (p.1.val % 3))) % 3),
    by
      have hj := p.1.isLt
      have ha := p.2.isLt
      omega⟩

theorem address_injective : Function.Injective address := by
  intro x y h
  have h101 : x.val % 101 = y.val % 101 :=
    congrArg (fun p : Fin 101 × Fin 3 => p.1.val) h
  have h3 : x.val % 3 = y.val % 3 :=
    congrArg (fun p : Fin 101 × Fin 3 => p.2.val) h
  have hx := x.isLt
  have hy := y.isLt
  apply Fin.ext
  omega

theorem inverse_right (p : Fin 101 × Fin 3) : address (inverse p) = p := by
  apply Prod.ext
  · apply Fin.ext
    have hj := p.1.isLt
    have ha := p.2.isLt
    change
      ((p.1.val + 101 * ((2 * (p.2.val + 3 - p.1.val % 3)) % 3))) % 101 =
        p.1.val
    omega
  · apply Fin.ext
    have hj := p.1.isLt
    have ha := p.2.isLt
    change
      ((p.1.val + 101 * ((2 * (p.2.val + 3 - p.1.val % 3)) % 3))) % 3 =
        p.2.val
    omega

theorem inverse_left (n : Fin 303) : inverse (address n) = n := by
  apply address_injective
  exact inverse_right (address n)

theorem address_bijective : Function.Bijective address :=
  ⟨address_injective, fun p => ⟨inverse p, inverse_right p⟩⟩

end Edgewalk.CRT
