from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService


class Driver:
	def __init__(self):
		self.driver = None

	def set_chrome(self):
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--lang=ko-KR")
		chrome_options.add_argument("--disable-blink-features=AutomationControlled")
		chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
		chrome_options.add_experimental_option('useAutomationExtension', False)
		chrome_options.add_argument("disable-infobars")
		user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
		chrome_options.add_argument(f"user-agent={user_agent}")

		self.driver = webdriver.Chrome(options=chrome_options)

		self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
			"source": """
				Object.defineProperty(navigator, 'webdriver', {
					get: () => undefined
				});
			"""
		})

		self.driver.execute_script("""
			window.onbeforeunload = null;
			window.addEventListener('beforeunload', function(event) {
				event.preventDefault();
				event.returnValue = '';
			});
		""")

		self.driver.execute_cdp_cmd('Browser.grantPermissions', {
			'permissions': ['clipboardReadWrite'],
		})

		return self.driver
