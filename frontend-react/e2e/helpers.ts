let _uniquePhoneCounter = 0;

export function uniquePhone(): string {
  // 10-digit, starting with 9, unique enough per test run to avoid 409 conflicts. A trailing
  // in-process counter (not just Date.now()) matters here: two calls back-to-back with no
  // await between them can land in the same millisecond and otherwise collide.
  _uniquePhoneCounter = (_uniquePhoneCounter + 1) % 100;
  const suffix = String(_uniquePhoneCounter).padStart(2, "0");
  return "9" + String(Date.now()).slice(-7) + suffix;
}
