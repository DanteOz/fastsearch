export function secToHMS(sec: number): string {
  return new Date(sec * 1000).toISOString().slice(11, 19);
}
