# Seva Mithra - Python Flask Service Marketplace

Updated version with:
- Seva Mithra branding
- User registration
- Service Provider registration
- Real login with password hashing
- SQLite database
- User dashboard
- Provider dashboard
- Admin dashboard
- Booking creation
- Provider accept/reject/complete
- User cancellation
- Ratings and reviews
- User/provider profile editing
- Admin users/providers/bookings/services/reviews pages
- Tutor category
- Working dashboard navigation buttons

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Demo accounts

User: user@demo.com / 123456
Provider: provider@demo.com / 123456
Admin: admin@sevamithra.com / admin123

The SQLite database `seva_mithra.db` is created automatically on first run.


## Login role buttons

The User, Service Provider and Admin buttons on the login screen are normal Flask links:
- `/login?role=user`
- `/login?role=provider`
- `/login?role=admin`

They do not depend on JavaScript, so all three tabs work reliably.


## Provider Search & Comparison

Customers can now:
1. Search for a specific service.
2. See all matching service providers.
3. Compare rating, experience, qualification, work specialization, location, pricing and contact.
4. Select a specific provider and book that provider.
5. The database is seeded with 3 dummy providers for every main service.

Dummy provider passwords are not intended for production; they use the demo password `demo123456`.


## UI update
- Added supplied Seva Mithra logo as a background/hero visual.
- Homepage is centered around the logo and search interface.
- Removed the large "Trusted professionals near you" provider preview from the homepage.
- Added animated gradients, floating shapes, glow effects, logo motion and service-card hover animations.
- Provider search, login, registration and dashboard functionality remains intact.


## V7 Visual Update
- The newly supplied Seva Mithra logo is used as the main brand image.
- A large, centered, subtle logo watermark now sits behind the homepage welcome quotation.
- Animated colorful background orbs and floating dots run behind every page.
- Buttons across the website have hover lift, shine, glow and press animations.
- Cards, inputs, navigation links and page sections have subtle attraction animations.
- The functional search, provider comparison, booking, login, registration and dashboards are preserved.


## V8 UI
- Uses only the newly uploaded Seva Mithra logo.
- Old image assets were removed from the static folder.
- The logo is a centered, subtle animated background behind the welcome interface.
- Added colorful animated background layers, floating orbs, button glow/hover/press effects, card hover effects and animated search controls.
- Existing service search, provider comparison, booking, registration, login and dashboards are preserved.
