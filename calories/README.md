# CALories - UC Berkeley Dining Nutrition Tracker

A web application that helps UC Berkeley students track their dining hall meal nutrition by scraping real-time data from Berkeley's dining website.

**[Live Demo](https://cal-dining-tracker.onrender.com)**
*Multi-food selection with custom serving sizes and combined nutritional totals*

## Features

- **Real-time nutrition data** - Scrapes current menu items from all UC Berkeley dining halls
- **Multi-food meal tracking** - Select multiple items and customize serving sizes
- **Combined nutrition totals** - Automatically calculates total calories, protein, fat, etc.
- **Search & filter** - Quickly find foods by name or category
- **Allergen warnings** - Displays combined allergens from all selected foods
- **Smart caching** - 1-hour TTL reduces server load and improves performance

## Technical Highlights

### Backend
- **Web scraping** - Reverse-engineered AJAX endpoints to bypass dynamic content loading
- **Flask REST API** - Clean API design with error handling and parameter validation
- **Lazy loading** - Nutrition data fetched on-demand rather than upfront
- **Intelligent caching** - Thread-safe caching system with configurable TTL

### Frontend
- **Responsive design** - Works on desktop and mobile
- **Asynchronous JavaScript** - Non-blocking API calls with async/await
- **Dynamic UI** - Real-time search filtering and interactive checkboxes
- **Berkeley branding** - Uses official Cal colors (Berkeley Blue #003262, California Gold #FDB515)

## Tech Stack

**Backend:** Python, Flask, BeautifulSoup, Requests
**Frontend:** JavaScript (ES6+), HTML5, CSS3
**Data Source:** UC Berkeley Dining (dining.berkeley.edu)

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip

### Run Locally

1. Clone the repository
```bash
git clone https://github.com/owenhughes-bit/cal-dining-tracker.git
cd cal-dining-tracker
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python app.py
```

4. Open your browser
```
http://localhost:5000
```

## Project Structure
```
calories/
├── backend/
│   ├── __init__.py
│   └── scraper.py          # Web scraping & caching logic
├── static/
│   └── styles.css          # Styling
├── templates/
│   └── index.html          # Frontend interface
├── app.py                  # Flask application & API routes
└── requirements.txt        # Python dependencies
```

## How It Works

1. **Initial Load** - User selects dining hall and meal period
2. **Food Display** - All available foods are fetched and displayed with search functionality
3. **Selection** - User checks food items and adjusts serving sizes
4. **Calculation** - App fetches nutrition data for each item and multiplies by serving size
5. **Results** - Combined totals are displayed with allergen warnings

## API Endpoints

- `GET /api/halls` - Returns list of dining halls
- `GET /api/periods?hall=<hall>` - Returns meal periods for a hall
- `GET /api/foods?hall=<hall>&period=<period>` - Returns all foods for a meal
- `GET /api/nutrition?hall=<hall>&period=<period>&category=<category>&food=<food>` - Returns nutrition info

## Challenges & Solutions

**Challenge:** Berkeley's dining website loads menu data dynamically via AJAX
**Solution:** Analyzed network requests to identify the hidden API endpoint and replicated the request structure

**Challenge:** Fetching nutrition for 100+ items would be too slow
**Solution:** Implemented lazy loading - only fetch nutrition when user actually selects an item

**Challenge:** Repeated requests would hammer the server
**Solution:** Built thread-safe caching system with 1-hour TTL to minimize redundant scraping

## Future Improvements

- [ ] User accounts to save favorite meals
- [ ] Daily nutrition goals tracking
- [ ] Export meal data as CSV
- [ ] Mobile app version
- [ ] Integration with CalCentral

## Known Issues

- Nutrition data may be unavailable for some items (depends on Berkeley's data)
- App "wakes up" slowly on first visit if deployed on free tier (Render sleeps after 15min inactivity)

## License

MIT License - feel free to use this project for learning!

## Acknowledgments

- Data source: UC Berkeley Dining Services
- Built as a portfolio project for technical club applications

## Contact

**Your Name**
- GitHub: [@owenhughes-bit](https://github.com/owenhughes-bit)
- Email: owen.hughes@berkeley.edu

---

*Note: This is an independent project and is not officially affiliated with UC Berkeley.*