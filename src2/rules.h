#ifndef RULES_H
#define RULES_H

#ifdef __cplusplus
extern "C" {
#endif

// Fast batch evaluation function.
// All input arrays have length num_players.
// It returns integer offer IDs (0 = discount, 1 = first_purchase_bonus, 
// 2 = regular_offer, 3 = special_reward, 4 = default_offer)
// The output is written to the offers array (of length num_players).
void evaluate_offers_batch_fast(
    int num_players,
    const int* levels, const int* days_since_last_purchase,
    const int* matches_lost, const int* has_spent_money,
    int num_rules,
    const int* min_levels, const int* max_levels,
    const int* min_days, const int* max_days,
    const int* min_matches, const int* max_matches,
    const int* spending_conditions,
    const double* weights,
    int* offers  // output array of ints
);

#ifdef __cplusplus
}
#endif

#endif
