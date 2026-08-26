// Broad catch that re-issues every failed charge with no transient allowlist.
export async function chargeCard(payment) {
  try {
    return await gateway.charge(payment);
  } catch (error) {
    return chargeCard(payment);
  }
}
