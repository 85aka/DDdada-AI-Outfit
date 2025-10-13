$(document).ready(function() {
    // 將取得天氣的邏輯封裝成一個函式
    function getWeatherForCity(city) {
        $.post("/weather", { city: city }, function(data) {
            let htmlContent = "";
            data.forEach(dayWeather => {
                htmlContent += `
                    <div class="daily-weather">
                        <div class="r1">
                            <span class="daily-date">${dayWeather.date}</span>
                            <span class="chinese-date">${dayWeather.day}</span>
                        </div>
                        <div class="r2">
                            <span class="daily-temperature">${dayWeather.temperature}°</span>
                            <span id="rain">☂</span>
                            <span class="rain-chance">${dayWeather.rain_chance}%</span>
                        </div>
                    </div>
                `;
            });
            $("#weather-data").html(htmlContent);
        });
    }

    // 頁面載入時立即取得新北市的天氣
    getWeatherForCity('新北市');

    

    // 若使用者更改下拉選單的選擇，也可取得新城市的天氣
    $("#city-dropdown").change(function() {
        var selectedCity = $(this).val();
        getWeatherForCity(selectedCity);
    });
});


