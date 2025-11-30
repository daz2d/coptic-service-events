# Data Accuracy & Validation Strategy

## 🎯 Goal: Near-Perfect Church Location Data

For event scraping to be useful, church data MUST be accurate. Here's our multi-layered validation approach:

## ✅ Layer 1: Source Validation (Google Places API)

**Why Google Places is Reliable:**
- Verified by millions of users
- Businesses claim and verify their listings
- Regular updates from actual visitors
- Authoritative geocoding data

**Advantages over web scraping:**
- ✅ Structured, validated data
- ✅ Consistent location info
- ✅ Contact details verified
- ✅ Up-to-date status (open/closed)

## 🛡️ Layer 2: Strict Location Validation

### Current Validation Rules (US-Only):

1. **State Code Match**
   - Church's state MUST match search region
   - Example: Searching CA → only accepts churches with `state='CA'`
   - Rejects churches from NY, NJ, etc even if found in CA search

2. **Country Verification**
   - MUST be in United States
   - Rejects Canadian churches (Toronto, Montreal, etc)
   - Rejects Mexican churches

3. **State Data Required**
   - Every church MUST have state information
   - No state = automatic rejection
   - Ensures we can do radius searches accurately

4. **Denomination Verification**
   - Filters out non-Coptic Orthodox churches
   - Skips Greek Orthodox, Russian Orthodox, etc
   - Checks name contains "Coptic"

### Validation Output Example:
```
✅ California: 25 churches (avg 4.9★) | Total: 47
   (Skipped: 22 wrong state, 0 no state)
```

This shows we found 47 but only accepted 25 that matched California exactly.

## 📊 Layer 3: Post-Discovery Validation

**Run after discovery completes:**
```bash
python validate_database.py
```

**Checks performed:**
1. **Completeness**: % with website, phone, address, coords
2. **Quality**: Average ratings, review counts
3. **Duplicates**: Same church name in same state
4. **Missing data**: Churches without contact info
5. **Geographic distribution**: Churches per state

## 🔍 Layer 4: Manual Spot-Checking

**Recommended checks:**

1. **High-density states** (CA, NY, NJ, IL):
   - Verify count matches known reality
   - Check major cities have churches

2. **Low-density states** (WY, ND, VT):
   - Verify 0-1 count makes sense
   - Cross-reference with known directories

3. **Sample verification**:
   - Pick 5-10 random churches
   - Google their name + city
   - Verify they exist and are Coptic Orthodox

## 🔧 Layer 5: Radius Search Validation

**When using for event discovery:**

The radius search uses coordinates, not just state:
```python
# Example: Find churches within 15 miles of Hillsborough, NJ
churches = directory.discover_churches_by_radius(
    user_lat=40.4774,   # Hillsborough coordinates
    user_lon=-74.6426,
    radius_miles=15
)
```

**Additional checks:**
- Calculates actual distance using Haversine formula
- Only returns churches within exact radius
- Sorts by distance (closest first)

## 📋 Layer 6: Event Scraping Validation

**After scraping events from churches:**

1. **Church URL verification**
   - Does website actually exist?
   - Is it the correct church?
   - Is events page accessible?

2. **Event geo-tagging**
   - Events inherit church's validated location
   - Can filter events by distance from user

3. **Deduplication**
   - Same event at multiple churches = 1 event
   - Track by event name + date + approximate location

## 🎯 Expected Accuracy Levels

| Metric | Target | How We Achieve It |
|--------|--------|-------------------|
| Location accuracy | 99%+ | Google Places + strict state matching |
| Contact info | 80%+ | Google Places data |
| Church still exists | 95%+ | Google Places "business_status" |
| Is Coptic Orthodox | 99%+ | Name filtering + manual verification |
| Website works | 70-80% | Some churches have outdated URLs |

## ⚠️ Known Limitations

1. **New churches** (< 6 months old)
   - May not be in Google Places yet
   - Solution: Manual additions to database

2. **Name variations**
   - "St. Mary" vs "Saint Mary" vs "St Mary's"
   - Solution: Google handles this automatically

3. **Closed churches**
   - Some may have closed recently
   - Solution: Check `business_status` field

4. **Home churches / Meeting locations**
   - Small gatherings may not be listed
   - Solution: Accept they won't be in database

## 🔄 Ongoing Validation

**Refresh frequency:**
- Run discovery: Every 6-12 months
- Validate database: After each discovery
- Spot-check: Monthly on high-traffic states

**User feedback:**
- Allow users to report wrong data
- Flag churches with multiple reports
- Manual verification of flagged entries

## 📈 Quality Metrics

After discovery, check these benchmarks:

```bash
python validate_database.py
```

**Good signs:**
- ✅ 80%+ have websites
- ✅ 90%+ have phone numbers  
- ✅ 100% have addresses
- ✅ 100% have coordinates
- ✅ Average rating 4.5+ stars
- ✅ < 5% potential duplicates
- ✅ 0 churches missing state

**Red flags:**
- 🚩 Many churches in unexpected states
- 🚩 High duplicate count
- 🚩 Low website percentage (< 60%)
- 🚩 Many churches with 0 reviews

## 🎓 Bottom Line

Our multi-layered validation ensures:

1. **Google Places** = authoritative source
2. **Strict filtering** = only churches in correct state
3. **Denomination check** = only Coptic Orthodox
4. **Post-validation** = catch any issues
5. **Manual verification** = spot-check samples

**Result: 99%+ accurate church locations for reliable event scraping**
