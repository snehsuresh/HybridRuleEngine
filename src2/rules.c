#include "rules.h"
#include <string.h>
#include <omp.h>

// Internal helper: Evaluate one player's offer using the fast method.
static int select_offer_fast(int level, int days_since_last_purchase, int matches_lost, int has_spent_money,
                               int num_rules,
                               const int* min_levels, const int* max_levels,
                               const int* min_days, const int* max_days,
                               const int* min_matches, const int* max_matches,
                               const int* spending_conditions,
                               const double* weights) {
    double best_weight = -1.0;
    int best_rule_index = -1;
    // Hint to enable vectorization on the loop.
    #pragma clang loop vectorize(enable) interleave(enable)
    for (int i = 0; i < num_rules; i++) {
        if (level < min_levels[i] || level > max_levels[i])
            continue;
        if (days_since_last_purchase < min_days[i] || days_since_last_purchase > max_days[i])
            continue;
        if (matches_lost < min_matches[i] || matches_lost > max_matches[i])
            continue;
        if (spending_conditions[i] != -1 && spending_conditions[i] != has_spent_money)
            continue;
        if (weights[i] > best_weight) {
            best_weight = weights[i];
            best_rule_index = i;
        }
    }
    if (best_rule_index == -1)
        return 4;  // 4 means "default_offer"
    // For demonstration, we return (rule index mod 4) as the offer id.
    return best_rule_index % 4;
}

// Batch function with internal OpenMP parallelization.
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
    int* offers  // output array
) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < num_players; i++) {
        offers[i] = select_offer_fast(
            levels[i],
            days_since_last_purchase[i],
            matches_lost[i],
            has_spent_money[i],
            num_rules,
            min_levels, max_levels,
            min_days, max_days,
            min_matches, max_matches,
            spending_conditions,
            weights
        );
    }
}
