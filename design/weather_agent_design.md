# Weather Agent Design

## Overview
This design document outlines the implementation of a weather agent using PydanticAI. The agent will provide weather information for locations using natural language queries.

## Components

### Dependencies
- `requests`: For making HTTP requests
- `pydantic_ai`: For building the AI agent
- `pydantic`: For data modeling

### Core Classes

1. `WeatherDependencies` (dataclass)
   - Contains any configuration needed for API calls

2. `WeatherResponse` (Pydantic Model)
   - temperature: float
   - response: str

### Tools

1. `get_lat_lng`
   - Input: location_description (str)
   - Output: dict with lat/lng
   - Uses open-meteo geocoding API: https://geocoding-api.open-meteo.com/v1/search

2. `get_weather`
   - Input: lat (float), lng (float)
   - Output: dict with weather data
   - Uses open-meteo weather API: https://api.open-meteo.com/v1/forecast
   - Returns current temperature and wind speed

## Implementation Plan

1. Set up project structure and dependencies
2. Implement core data models
3. Implement tools using open-meteo APIs
4. Create agent with proper system prompt
5. Add example usage

## Testing Strategy

- Unit tests for data models
- Integration tests for API calls
- End-to-end tests for full agent workflow

## Future Improvements

- Add more weather data points (humidity, wind, etc)
- Cache frequent location queries
- Add error handling for API failures 