/**
 * SessionEditor - exercise list management
 * The session creation UI is implemented directly in PlansTab's AddSessionModal
 * for tight coupling with plan state. This file serves as domain documentation.
 */

export const EMPTY_EX = { name: '', sets: 3, reps: 10, rest_seconds: 60 };

export function buildSessionPayload(form) {
  return {
    ...form,
    exercises: form.exercises.map(ex => ({
      ...ex,
      sets: Number(ex.sets),
      reps: Number(ex.reps),
      rest_seconds: Number(ex.rest_seconds),
    })),
  };
}
