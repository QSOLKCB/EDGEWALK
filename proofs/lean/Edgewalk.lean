import Edgewalk.CRT
import Edgewalk.Phase
import Edgewalk.Monomial
import Edgewalk.GF2

/-! These are typed proof obligations: theorem names alone are insufficient. -/

example : Function.Bijective Edgewalk.CRT.address :=
  Edgewalk.CRT.address_bijective

example (p : Fin 101 × Fin 3) :
    Edgewalk.CRT.address (Edgewalk.CRT.inverse p) = p :=
  Edgewalk.CRT.inverse_right p

example (a : Fin 3) :
    Edgewalk.Phase.exponent a +
      Edgewalk.Phase.exponent (Edgewalk.Phase.nextFibre a) +
      Edgewalk.Phase.exponent
        (Edgewalk.Phase.nextFibre (Edgewalk.Phase.nextFibre a)) = 0 :=
  Edgewalk.Phase.three_step_closure a

example :
    (∀ s : Edgewalk.Monomial.State,
      Edgewalk.Monomial.iterateStep 303 s = s) ∧
    (∀ k : Nat, 0 < k → k < 303 →
      ∃ s : Edgewalk.Monomial.State,
        Edgewalk.Monomial.iterateStep k s ≠ s) :=
  Edgewalk.Monomial.monomial_exact_order_303

example (x : Edgewalk.GF2.Bit) : x + x = 0 :=
  Edgewalk.GF2.self_add_zero x
