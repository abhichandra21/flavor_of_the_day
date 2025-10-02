# Screenshots Guide

## Adding Screenshots to the Repository

To complete the README, you need to add the following 4 screenshot images to the `docs/images/` directory:

### Required Screenshots

1. **`integration-dashboard.png`**
   - Screenshot of the Home Assistant integration dashboard showing multiple configured locations
   - Should show the "Flavor of the Day" integration with 5 devices/entities
   - Shows: Culver's - Hartland WI, Culver's - Waukesha WI, Kopp's - Greenfield, Oscar's - West Allis, Goodberry's - Raleigh

2. **`provider-selection.png`**
   - Screenshot of the provider selection dialog
   - Shows: Dropdown with "Culver's" selected
   - Title: "Select Provider"
   - Subtitle: "Choose the ice cream store chain to track flavors for."

3. **`location-search.png`**
   - Screenshot of the location search dialog
   - Shows: Text input for "City or ZIP Code"
   - Optional "State" dropdown
   - Title: "Search for Location"
   - Subtitle: "Enter the city or ZIP code to find nearby locations."

4. **`location-selection.png`**
   - Screenshot of the location selection dialog
   - Shows: Dropdown with 25 locations found
   - Selected: "Culver's - Waukesha, WI - E Main St - Waukesha"
   - Optional "Custom Name" field
   - "Update Interval (minutes)" field showing "30 minutes"
   - Title: "Select Location"
   - Subtitle: "Found 25 locations. Select your preferred location."

## How to Add the Screenshots

### Method 1: Save from your screenshots
1. Take screenshots from your Home Assistant instance
2. Crop them to show just the relevant dialog/view
3. Save them with the exact filenames listed above
4. Place them in `docs/images/` directory

### Method 2: Export from browser
1. Open the dialogs in your Home Assistant UI
2. Use browser developer tools to capture element screenshots
3. Save with the correct filenames
4. Place in `docs/images/` directory

## File Checklist

```
docs/
└── images/
    ├── integration-dashboard.png
    ├── provider-selection.png
    ├── location-search.png
    └── location-selection.png
```

## Recommended Image Specifications

- **Format**: PNG (for transparency support)
- **Width**: 800-1200px (will be resized in README to 400px wide)
- **Quality**: High quality, clear text
- **Background**: Dark mode recommended (matches most HA themes)
- **File size**: Keep under 500KB each for fast loading

## After Adding Images

1. Verify images are in the correct location
2. Commit the images: `git add docs/images/*.png`
3. Push to GitHub: `git push origin main`
4. View the README on GitHub to confirm images display correctly

## Alternative: Use Relative Links to GitHub

If you prefer, you can also reference the images directly from your GitHub repository:

```markdown
<img src="https://raw.githubusercontent.com/abhichandra21/ha-flavoroftheday/main/docs/images/integration-dashboard.png" alt="Integration Dashboard" width="400"/>
```

This works even before the images are committed, as long as you push them to GitHub.