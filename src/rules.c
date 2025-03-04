#include "rules.h"
#include <string.h>

const char* select_offer(int level, int days_since_last_purchase, int matches_lost, int has_spent_money,
                         int num_rules,
                         const int* min_levels, const int* max_levels,
                         const int* min_days, const int* max_days,
                         const int* min_matches, const int* max_matches,
                         const int* spending_conditions,
                         const double* weights) {
    double best_weight = -1.0;
    int best_rule_index = -1;

    for (int i = 0; i < num_rules; i++) {
        if (level < min_levels[i] || level > max_levels[i]) continue;
        if (days_since_last_purchase < min_days[i] || days_since_last_purchase > max_days[i]) continue;
        if (matches_lost < min_matches[i] || matches_lost > max_matches[i]) continue;
        if (spending_conditions[i] != -1 && spending_conditions[i] != has_spent_money) continue;

        if (weights[i] > best_weight) {
            best_weight = weights[i];
            best_rule_index = i;
        }
    }

    if (best_rule_index == -1)
        return "default_offer";

    static const char* offers[] = {
        "discount", "first_purchase_bonus", "regular_offer", "special_reward"
    };
    return offers[best_rule_index % 4];
}

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
) {
    for (int i = 0; i < num_players; i++) {
        const char* offer = select_offer(
            levels[i], days_since_last_purchase[i], matches_lost[i], has_spent_money[i],
            num_rules,
            min_levels, max_levels, min_days, max_days, min_matches, max_matches,
            spending_conditions, weights
        );
        strncpy(offers[i], offer, 31);
        offers[i][31] = '\0';
    }
}
