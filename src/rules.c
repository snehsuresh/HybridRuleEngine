#include "rules.h"
#include <string.h>

const char* evaluate_offer(
    int level, int days_since_last_purchase, int matches_lost, int has_spent_money,
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

    // For demonstration, select one of a few offers based on rule index.
    static char offer[32];
    const char* offers[] = {
        "discount", "first_purchase_bonus", "regular_offer", "special_reward"
    };
    // Here we pick an offer from our offers array. In a real system, the offer might be part of the rule.
    strcpy(offer, offers[best_rule_index % 4]);
    return offer;
}
