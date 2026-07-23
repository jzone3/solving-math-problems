/- Throwaway pipeline test: include_str + LRAT parser + verified checker. -/
import Std.Tactic.BVDecide

open Std.Sat Std.Tactic.BVDecide

def tinyCnf : CNF Nat := ⟨#[[(0, true)], [(0, false)]]⟩

def tinyLrat : String := include_str "../cert/tiny.lrat"

def tinyCert : Array LRAT.IntAction :=
  match LRAT.parseLRATProof tinyLrat.toUTF8 with
  | .ok c => c
  | .error _ => #[]

def tinyOk : Bool := LRAT.check tinyCert tinyCnf

theorem tinyOk_true : tinyOk = true := by native_decide

theorem tiny_unsat : tinyCnf.Unsat := LRAT.check_sound tinyCert tinyCnf tinyOk_true
