import requests
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import nest_asyncio

#use this to run the agent in jupyter notebook
nest_asyncio.apply()

# --------------------------------------------------------------
# Define the Structured Response
# --------------------------------------------------------------

class WeatherResponse(BaseModel):
    """Structured response from the weather agent."""
    temperature: float = Field(description="The current temperature in celsius")
    response: str = Field(description="Natural language response to the user's query")

# --------------------------------------------------------------
# Define the weather agent
# --------------------------------------------------------------

weather_agent = Agent(
    'gpt-4o-mini',
    system_prompt="You are a helpful weather assistant.",
    result_type=WeatherResponse,    
)

# --------------------------------------------------------------
# Define the tool to get weather
# --------------------------------------------------------------

@weather_agent.tool
def get_weather(ctx: RunContext[None], latitude: float, longitude: float):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]

# --------------------------------------------------------------
# Run the weather agent
# --------------------------------------------------------------

#agent is ran in sync mode, basically run until it's done
result = weather_agent.run_sync("What's the weather like in Paris today?")
print(f"Temperature: {result.data.temperature}°C")
print(f"Response: {result.data.response}")