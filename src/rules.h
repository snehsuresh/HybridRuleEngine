#ifndef RULES_H
#define RULES_H

#ifdef __cplusplus
extern "C" {
#endif

// Evaluate offer for a player using data-driven rules passed from Python.
// Parameters:
//   level: player's level.
//   days_since_last_purchase: number of days since the last purchase.
//   matches_lost: number of matches lost.
//   has_spent_money: 0 if never spent, 1 if has spent.
//   num_rules: number of rules in the array.
//   min_levels, max_levels: arrays defining level boundaries.
//   min_days, max_days: arrays defining purchase recency boundaries.
//   min_matches, max_matches: arrays defining matches lost boundaries.
//   spending_conditions: array for spending condition (-1 means ignore).
//   weights: array with a weight (score) for each rule.
// Returns a pointer to a constant string indicating the selected offer.
const char* evaluate_offer(
    int level, int days_since_last_purchase, int matches_lost, int has_spent_money,
    int num_rules,
    const int* min_levels, const int* max_levels,
    const int* min_days, const int* max_days,
    const int* min_matches, const int* max_matches,
    const int* spending_conditions,
    const double* weights);

#ifdef __cplusplus
}
#endif

#endif
