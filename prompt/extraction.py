OPENAI_EXTRACTION_PROMPT = """
From the given input, please extract:
- Target number of people for all companies, if not specified, default to 10
    - If given a range, use the lower bound
- Key industry to search for
- Companies to search for, if not specified, default to "any"
- Specific locations, if not specified, default to "any"
- Implied job positions, if not specified or not a role-based word, default to "". Industry to be excluded from the position string.
- If canadian people mentioned, then include_cad_schools_on_fill_search should be true

Return a JSON with the following structure:
{
    "target_total": int,
    "keyword_industry": str,
    "companies": [
        {
            "name": str,
            "locations": [
                {
                    "location": str,
                    "target_per_location": int
                }
            ]
        }
    ],
    "additional_filters": {
        "positions": [str],
        "include_cad_schools_on_fill_search": bool
    }
}
"""

POST_PROMPT_INSTR = """
    Requirements:
    - Include all companies and locations in the search.
    - For each location, automatically set each location to 10 (even for "any"), regardless of what is specified in the input.
"""