# Prompt Version Registry

This directory contains versioned prompts for all agents.

## Structure
- `v1/` - Current production prompts (initial version)

## Guidelines
1. **Never edit prompts in-place** - Create a new version
2. **Document changes** in `changelog.md`
3. **Run eval tests** before promoting new version
4. **Keep prompts backwards-compatible** when possible

## Version Naming
- `v1`, `v2`, etc. for major changes
- Use feature flags for A/B testing prompts
