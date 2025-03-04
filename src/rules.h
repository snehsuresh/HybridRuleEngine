#ifndef RULES_H
#define RULES_H

#ifdef __cplusplus
extern "C" {
#endif

// Evaluate offer for a player using data‑driven rules.
// Parameters:
//   level: player's level.
//   days_since_last_purchase: number of days since the last purchase.
//   matches_lost: number of matches lost.
//   has_spent_money: 0 if never spent, 1 if has spent.
// Returns a pointer to a constant string indicating the selected offer.
const char* evaluate_offer(int level, int days_since_last_purchase, int matches_lost, int has_spent_money);

#ifdef __cplusplus
}
#endif

#endif
