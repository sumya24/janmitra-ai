export function uniquePhone(): string {
  // 10-digit, starting with 9, unique enough per test run to avoid 409 conflicts.
  return "9" + String(Date.now()).slice(-9);
}
