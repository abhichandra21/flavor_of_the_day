# TODO - Flavor of the Day Integration

## High Priority

### 1. Re-enable mypy Type Checking
**Status:** Disabled in tox.ini
**Effort:** Medium
**Description:** Mypy was temporarily disabled to unblock development. Need to fix ~40 type checking errors.

**Files affected:**
- `tox.ini` - Uncomment `[testenv:mypy]` section
- `requirements-dev.txt` - Uncomment `mypy>=1.0.0`
- `pyproject.toml` - Add mypy back to `env_list`

**Main errors to fix:**
- `sensor.py` - FlavorUpdateCoordinator typing issues (dict vs FlavorInfo)
- `config_flow.py` - FlowResult return type mismatches
- `__init__.py` - Abstract class instantiation and MappingProxyType issues
- `providers/*.py` - Method signature overrides (get_upcoming_flavors)
- `providers/base.py` - Type annotations for _last_request_time dict
- `providers/kopps.py` - as_utc() None handling

**References:**
- See last tox mypy run output for full list of errors
- gasbuddy has similar mypy config and passes cleanly

---

## Medium Priority

### 2. Improve Test Coverage for Providers
**Status:** Current coverage 25-35%
**Target:** 70%+
**Effort:** Medium-High

**Current coverage by provider:**
- `culvers.py`: 31%
- `goodberrys.py`: 35%
- `kopps.py`: 25%
- `oscars.py`: 33%
- `base.py`: 47%

**What's needed:**
- Mock HTTP requests using `aioresponses`
- Test location search functionality
- Test flavor data parsing
- Test error handling (timeouts, network errors, invalid responses)
- Test rate limiting logic
- Test upcoming flavors functionality

**Example test structure:**
```python
async def test_culvers_search_locations(aioresponses):
    """Test Culver's location search."""
    aioresponses.get(
        "https://api.culvers.com/locations",
        payload={"locations": [...]},
    )
    # Test implementation
```

---

### 3. Add Home Assistant Brands Integration
**Status:** Not added
**Effort:** Low
**Description:** Add custom icon/logo for the integration in Home Assistant UI.

**Steps:**
1. Create icon assets (512x512 PNG)
2. Fork https://github.com/home-assistant/brands
3. Add icon to `custom_integrations/flavor_of_the_day/`
4. Submit PR following https://hacs.xyz/docs/publish/include#check-brands

**Resources:**
- HACS brands documentation: https://hacs.xyz/docs/publish/include#check-brands
- Home Assistant brand guidelines: https://brands.home-assistant.io/

---

## Low Priority

### 4. Increase Overall Coverage Threshold
**Status:** Currently set to 50%
**Target:** 80%
**Effort:** Medium

**What's needed:**
- Fix provider coverage (see #2)
- Add tests for coordinator error handling
- Add tests for services.py (currently 28%)
- Add tests for config flow error paths (currently 73%)

**File:** `pyproject.toml`
```toml
[tool.coverage.report]
fail_under = 80  # Currently 50
```

---

### 5. Add More Provider Support
**Status:** Currently supports 4 providers
**Effort:** Medium per provider

**Potential providers to add:**
- Rita's Italian Ice
- Dairy Queen (if they have FOTD program)
- Local/regional frozen custard shops
- Frozen yogurt chains with daily specials

**Template for new provider:**
1. Create `providers/provider_name.py`
2. Inherit from `BaseFlavorProvider`
3. Implement required methods
4. Add to `PROVIDER_CLASSES` in `__init__.py` and `config_flow.py`
5. Add tests
6. Update documentation

---

### 6. Documentation Improvements
**Status:** Minimal documentation
**Effort:** Low-Medium

**What's needed:**
- Comprehensive README.md with:
  - Screenshots of the integration in HA UI
  - Supported providers list with store locator links
  - Configuration examples
  - Service usage examples
  - Troubleshooting section
- Developer documentation:
  - How to add a new provider
  - Architecture overview
  - Testing guide
- User documentation:
  - Installation via HACS
  - Manual installation steps
  - FAQ section

---

## Technical Debt

### 7. Remove Duplicate/Unused Code
**Status:** Some cleanup needed
**Effort:** Low

**Items:**
- Remove unused type: ignore comments in `config_flow.py` (lines 175, 177)
- Clean up duplicate pylint disable rules in `pyproject.toml`
- Review and consolidate exception handling patterns

---

### 8. Enhance Error Messages
**Status:** Basic error handling
**Effort:** Low-Medium

**What's needed:**
- More descriptive error messages for users
- Better logging for debugging provider issues
- User-friendly error messages in config flow
- Helpful hints when location search fails

---

### 9. Performance Optimizations
**Status:** Not profiled
**Effort:** Low

**Potential improvements:**
- Cache location search results
- Optimize HTTP request patterns
- Consider connection pooling for providers
- Profile and optimize slow code paths

---

### 10. Add Integration Tests
**Status:** Only unit tests
**Effort:** Medium

**What's needed:**
- Test actual Home Assistant integration flow
- Test coordinator updates with real providers
- Test service calls end-to-end
- Test config flow with real API responses (using VCR.py or similar)

---

## Future Enhancements

### 11. Additional Features
**Ideas for future development:**

- **Multi-location support**: Track flavors from multiple stores simultaneously
- **Notifications**: Alert when favorite flavors are available
- **Calendar integration**: Show upcoming flavor schedule (for providers that publish it)
- **Historical data**: Track flavor history and statistics
- **Favorites**: Mark favorite flavors and get notifications
- **Images**: Display flavor images in HA dashboard (when available)
- **Nutritional info**: Show nutritional information (when available)

### 12. Automation Examples
**Create example automations:**
- Notify when a specific flavor is available
- Create a daily flavor announcement
- Track flavor change patterns
- Send weekly flavor summary

---

## Notes

### Service Name Change
The service was renamed from `force_refresh` to `refresh` during the test rewrite. This is a breaking change but acceptable since the integration is not yet widely used.

### Mypy Configuration
The integration uses gasbuddy's mypy configuration as a reference. When re-enabling mypy, ensure all type: ignore comments are reviewed and only used where necessary.

### Coverage Philosophy
Current 53% coverage is acceptable for initial release. Focus on covering critical paths (config flow, coordinator, sensor) first, then improve provider coverage over time.