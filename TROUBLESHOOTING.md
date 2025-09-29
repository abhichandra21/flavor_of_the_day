# Troubleshooting Guide for Flavor of the Day Integration

This guide provides solutions for common issues with the Flavor of the Day integration.

## Common Issues and Solutions

### 1. Location Not Found

**Problem**: The search returns "no_locations_found" error.

**Solutions**:
- Verify the spelling of the city name
- Use the state abbreviation (e.g., "WI" instead of "Wisconsin")
- Try searching with ZIP code instead of city name
- Check if the store location exists in the real world
- Some providers might not have online information for all locations

### 2. No Flavor Data Available

**Problem**: Sensor shows "Unknown" or no data.

**Solutions**:
- The store might not have updated their flavor of the day yet
- Some locations may not participate in the flavor of the day program
- The store might be closed
- Website structure might have changed (requires integration update)

### 3. Connection Errors

**Problem**: Receiving "connection_failed" or network errors.

**Solutions**:
- Check your Home Assistant network connectivity
- Some provider websites might be temporarily down
- Verify firewall settings allow external connections
- The provider might be blocking requests from your IP address

### 4. Slow Response Times

**Problem**: Long delays in getting flavor information.

**Solutions**:
- Increase the update interval in configuration
- The provider's website might be slow to respond
- Your network connection to the provider might be slow

### 5. Integration Fails to Load

**Problem**: Integration doesn't appear in the list when adding.

**Solutions**:
- Verify installation in the `custom_components` directory
- Check that all files were copied correctly
- Restart Home Assistant completely
- Check logs for installation errors

## Error Messages and Solutions

### "no_locations_found"
- **Cause**: No locations matching search criteria found
- **Solution**: Try different search terms, verify location exists

### "provider_error"
- **Cause**: Error communicating with the provider
- **Solution**: Check provider website status, verify location ID

### "connection_failed"
- **Cause**: Could not establish connection to location
- **Solution**: Network issues or location-specific problems

### "network_error"
- **Cause**: Network connectivity issue
- **Solution**: Check Home Assistant network connectivity

### "unknown_error"
- **Cause**: Unexpected error occurred
- **Solution**: Check logs for more details, report issue

## Debugging Steps

### 1. Check Logs
Enable debug logging to get more information:

```yaml
logger:
  default: warning
  logs:
    custom_components.flavor_of_the_day: debug
```

### 2. Test Manually
Visit the provider's website manually to verify if location and flavor information is available.

### 3. Verify Configuration
- Check if location ID is still valid
- Verify provider selection is correct
- Confirm update interval is appropriate

### 4. Network Testing
- Verify Home Assistant can access external websites
- Check if provider domains are blocked by firewall
- Test from different network if possible

## Known Limitations

### Provider-Specific Limitations
- **Culver's**: Some locations may not have online flavor information
- **Kopp's**: Availability may vary by season
- **Oscar's**: Limited location coverage
- **Goodberry's**: Limited to North Carolina locations

### Update Frequency
- Flavor information is only as current as the provider updates it
- Some providers may update their information multiple times per day
- Integration respects update interval but cannot control provider update timing

## When to Report Issues

Report issues in the GitHub repository when:

1. Following all troubleshooting steps doesn't resolve the issue
2. You suspect a bug in the integration code
3. A provider's website structure has changed
4. A location that should exist is not found
5. There are consistent connection errors to a provider

Include in your issue report:
- Home Assistant version
- Integration version
- Provider and location information
- Steps to reproduce the issue
- Relevant log entries
- Expected vs actual behavior

## Performance Tips

- Set appropriate update intervals (not too frequent to avoid being rate-limited)
- Only configure locations you actually need
- Monitor Home Assistant performance after adding multiple locations
- Use custom names to easily identify different locations in your setup