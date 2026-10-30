import Edgewalk.Phase

/-!
# ETQ-303 finite monomial step

A state is a 303-index support address and a Gaussian-unit phase exponent.
The phase is a discrete potential difference. The exact finite monomial
step is conjugate to the cyclic support shift. This is algebra only, not a
measured physical process or a proof about astronomical spacetime.
-/

namespace Edgewalk.Monomial

open Edgewalk.CRT Edgewalk.Phase

abbrev State := Fin 303 × ZMod 4

def supportPower (k : Nat) (n : Fin 303) : Fin 303 :=
  ⟨(n.val + k) % 303, Nat.mod_lt _ (by omega)⟩

def fibre (n : Fin 303) : Fin 3 := (address n).2

def step (s : State) : State :=
  (supportPower 1 s.1, s.2 + exponent (fibre s.1))

/-- Algebraic power formula, proved equal to iteration below. -/
def power (k : Nat) (s : State) : State :=
  (supportPower k s.1,
   s.2 + potential (fibre (supportPower k s.1)) - potential (fibre s.1))

def iterateStep : Nat → State → State
  | 0, s => s
  | k + 1, s => step (iterateStep k s)

theorem supportPower_zero (n : Fin 303) : supportPower 0 n = n := by
  apply Fin.ext
  change (n.val + 0) % 303 = n.val
  have hn := n.isLt
  omega

theorem supportPower_comp (m k : Nat) (n : Fin 303) :
    supportPower m (supportPower k n) = supportPower (m + k) n := by
  apply Fin.ext
  change ((n.val + k) % 303 + m) % 303 = (n.val + (m + k)) % 303
  omega

theorem supportPower_period (n : Fin 303) : supportPower 303 n = n := by
  apply Fin.ext
  change (n.val + 303) % 303 = n.val
  have hn := n.isLt
  omega

theorem supportPower_minimal (k : Nat) (hk : 0 < k) (hlt : k < 303) :
    supportPower k (0 : Fin 303) ≠ 0 := by
  intro h
  have hval : k % 303 = 0 := by
    have hv := congrArg Fin.val h
    simpa [supportPower] using hv
  omega

theorem fibre_step (n : Fin 303) :
    fibre (supportPower 1 n) = nextFibre (fibre n) := by
  apply Fin.ext
  change ((n.val + 1) % 303) % 3 = ((n.val % 3) + 1) % 3
  omega

theorem power_zero (s : State) : power 0 s = s := by
  rcases s with ⟨n, z⟩
  apply Prod.ext
  · exact supportPower_zero n
  · change z + potential (fibre (supportPower 0 n)) - potential (fibre n) = z
    rw [supportPower_zero]
    abel

theorem power_comp (m k : Nat) (s : State) :
    power m (power k s) = power (m + k) s := by
  rcases s with ⟨n, z⟩
  apply Prod.ext
  · change supportPower m (supportPower k n) = supportPower (m + k) n
    exact supportPower_comp m k n
  · change
      (z + potential (fibre (supportPower k n)) - potential (fibre n)) +
        potential (fibre (supportPower m (supportPower k n))) -
        potential (fibre (supportPower k n)) =
      z + potential (fibre (supportPower (m + k) n)) - potential (fibre n)
    rw [supportPower_comp]
    abel

theorem power_one (s : State) : power 1 s = step s := by
  rcases s with ⟨n, z⟩
  apply Prod.ext
  · rfl
  · change
      z + potential (fibre (supportPower 1 n)) - potential (fibre n) =
      z + exponent (fibre n)
    rw [fibre_step, exponent_is_potential_difference]
    abel

theorem power_succ (k : Nat) (s : State) :
    power (k + 1) s = step (power k s) := by
  calc
    power (k + 1) s = power 1 (power k s) := by
      simpa [Nat.add_comm] using (power_comp 1 k s).symm
    _ = step (power k s) := power_one _

theorem iterateStep_eq_power (k : Nat) (s : State) :
    iterateStep k s = power k s := by
  induction k with
  | zero =>
      change s = power 0 s
      exact (power_zero s).symm
  | succ k ih =>
      change step (iterateStep k s) = power (k + 1) s
      rw [ih]
      exact (power_succ k s).symm

theorem power_period (s : State) : power 303 s = s := by
  rcases s with ⟨n, z⟩
  apply Prod.ext
  · exact supportPower_period n
  · change
      z + potential (fibre (supportPower 303 n)) - potential (fibre n) = z
    rw [supportPower_period]
    abel

/-- Order exactly 303: total return and no smaller positive iterate is identity. -/
theorem monomial_exact_order_303 :
    (∀ s : State, iterateStep 303 s = s) ∧
    (∀ k : Nat, 0 < k → k < 303 → ∃ s : State, iterateStep k s ≠ s) := by
  constructor
  · intro s
    rw [iterateStep_eq_power]
    exact power_period s
  · intro k hk hlt
    refine ⟨((0 : Fin 303), (0 : ZMod 4)), ?_⟩
    intro h
    rw [iterateStep_eq_power] at h
    have hsupport : supportPower k (0 : Fin 303) = 0 := by
      exact congrArg Prod.fst h
    exact supportPower_minimal k hk hlt hsupport

end Edgewalk.Monomial
