#include "rules.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Structure for a rule – extended with weight and temporal conditions.
typedef struct {
    int min_level;
    int max_level;
    int min_days_since_last_purchase;
    int max_days_since_last_purchase;
    int min_matches_lost;
    int max_matches_lost;
    int has_spent_money; // -1 means ignore condition
    char offer[32];
    double weight;
    long start_time;
    long end_time;
} Rule;

#define MAX_RULES 100

static Rule rules[MAX_RULES];
static int num_rules = 0;
static int rules_loaded = 0;

// Helper: Read entire file into a buffer.
static char* read_file(const char* filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long len = ftell(fp);
    rewind(fp);
    char *buffer = (char*)malloc(len + 1);
    if (!buffer) { fclose(fp); return NULL; }
    fread(buffer, 1, len, fp);
    buffer[len] = '\0';
    fclose(fp);
    return buffer;
}

// A very simple parser for our known JSON format.
// This parser expects the JSON file to have the following fixed structure:
// {
//     "rules": [
//         { "min_level": <int>, "max_level": <int>, "min_days_since_last_purchase": <int>,
//           "max_days_since_last_purchase": <int>, "min_matches_lost": <int>, "max_matches_lost": <int>,
//           "has_spent_money": <int>, "offer": "<string>", "weight": <double>, "start_time": <long>, "end_time": <long> },
//         ... 100 rules ...
//     ]
// }
static void load_rules() {
    char *json = read_file("rules_config.json");
    if (!json) {
        fprintf(stderr, "Failed to open rules_config.json\n");
        exit(1);
    }

    // Find the start of the rules array.
    char *rules_array = strstr(json, "\"rules\":");
    if (!rules_array) {
        fprintf(stderr, "Invalid JSON format: missing \"rules\" key.\n");
        free(json);
        exit(1);
    }
    // Find the '[' that begins the array.
    char *array_start = strchr(rules_array, '[');
    if (!array_start) {
        fprintf(stderr, "Invalid JSON format: missing '['.\n");
        free(json);
        exit(1);
    }
    // Now, iterate over rule objects.
    char *ptr = array_start;
    num_rules = 0;
    while ((ptr = strchr(ptr, '{')) != NULL && num_rules < MAX_RULES) {
        // Find the closing brace for this object.
        char *end = strchr(ptr, '}');
        if (!end) break;
        // Temporarily terminate the string.
        *end = '\0';

        // Parse the rule using sscanf.
        // Note: This format string must match exactly the order in which keys appear in the file.
        Rule r;
        int scanned = sscanf(ptr,
            " \"min_level\" : %d ,"
            " \"max_level\" : %d ,"
            " \"min_days_since_last_purchase\" : %d ,"
            " \"max_days_since_last_purchase\" : %d ,"
            " \"min_matches_lost\" : %d ,"
            " \"max_matches_lost\" : %d ,"
            " \"has_spent_money\" : %d ,"
            " \"offer\" : \" %31[^\"]\" ,"
            " \"weight\" : %lf ,"
            " \"start_time\" : %ld ,"
            " \"end_time\" : %ld",
            &r.min_level, &r.max_level,
            &r.min_days_since_last_purchase, &r.max_days_since_last_purchase,
            &r.min_matches_lost, &r.max_matches_lost,
            &r.has_spent_money, r.offer,
            &r.weight, &r.start_time, &r.end_time);

        if (scanned == 11) {
            rules[num_rules++] = r;
        } else {
            fprintf(stderr, "Failed to parse rule: scanned %d fields\n", scanned);
        }
        // Move pointer past the end of this rule object.
        ptr = end + 1;
    }
    free(json);
    rules_loaded = 1;
    // For debugging, you might print num_rules.
    // printf("Loaded %d rules\n", num_rules);
}

// Evaluate all rules and select the matching rule with the highest weight.
const char* evaluate_offer(int level, int days_since_last_purchase, int matches_lost, int has_spent_money) {
    if (!rules_loaded) {
        load_rules();
    }
    time_t now = time(NULL);
    double best_weight = -1.0;
    int best_index = -1;

    for (int i = 0; i < num_rules; i++) {
        Rule r = rules[i];
        // Check temporal condition.
        if (now < r.start_time || now > r.end_time) {
            continue;
        }
        // Check level, days, matches conditions.
        if (level < r.min_level || level > r.max_level) continue;
        if (days_since_last_purchase < r.min_days_since_last_purchase || days_since_last_purchase > r.max_days_since_last_purchase) continue;
        if (matches_lost < r.min_matches_lost || matches_lost > r.max_matches_lost) continue;
        // Check spending condition (if not ignored).
        if (r.has_spent_money != -1 && r.has_spent_money != has_spent_money) continue;
        // This rule matches – use its weight as score.
        if (r.weight > best_weight) {
            best_weight = r.weight;
            best_index = i;
        }
    }
    if (best_index != -1) {
        return rules[best_index].offer;
    }
    return "default_offer";
}
