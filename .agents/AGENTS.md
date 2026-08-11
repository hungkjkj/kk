
### Custom Rules
- **Strict Rule:** NEVER use mock data when working with financial data. If an API call fails or data is missing, always fail explicitly (raise an exception) or return 0/None. Do NOT use hardcoded fake numbers.
