#ifndef RULES_H
#define RULES_H

#ifdef __cplusplus
extern "C" {
#endif

void evaluate_offers_batch(
    int num_players,
    const int* levels, const int* days_since_last_purchase,
    const int* matches_lost, const int* has_spent_money,
    int num_rules,
    const int* min_levels, const int* max_levels,
    const int* min_days, const int* max_days,
    const int* min_matches, const int* max_matches,
    const int* spending_conditions,
    const double* weights,
    char offers[][32] // Output array
);

#ifdef __cplusplus
}
#endif

#endif
