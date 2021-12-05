import re
import pandas as pd
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import datetime
from logger import logger

NUMBER_PAGES = 100


class Scraper:
    """
    basic scraper object
    """

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        logger.info("Initialized webdriver")

    def _prepare_link(self, number_days: int, keyword: str) -> str:
        """prepare link to download the requests

        Parameters
        ----------
        number_days : int
            number of days to look back in time
        keyword : str
            keyword used for searching

        Returns
        -------
        str
            consolidated link
        """
        self.number_days = number_days
        today = date.today()
        days = datetime.timedelta(number_days)
        start_date = today - days
        start_date = str(start_date)
        year_regex = r"(\d\d\d\d)-"
        year_only = re.findall(year_regex, start_date)[0]
        month_regex = r".....(..)"
        month_only = re.findall(month_regex, start_date)[0]
        day_regex = r"........(..)"
        day_only = re.findall(day_regex, start_date)[0]

        main_url = "http://www.consultaesic.cgu.gov.br/busca/SitePages/resultadopesquisa.aspx?k=ALL"
        aux_url = "%20DataPedido%3E%3D"

        final_link = (
            f"{main_url}({keyword}){aux_url}{day_only}%2F{month_only}%2F{year_only}"
        )
        return final_link

    def load_initial_page(self, number_days: int, keyword: str):
        """
        load initial page in the current browser session.

        Parameters
        ----------
        number_days : int
            number of days to look back in time
        keyword : str
            keyword used for searching
        """
        final_link = self._prepare_link(number_days, keyword)
        self.driver.get(final_link)
        time.sleep(2)

    def search_requests(self) -> List[str]:
        """search for requests
        
        Returns
        -------
        List[str]
            list with links to get the request information
        """
        list_of_links = []
        # try to open up to number_pages pages in order to find those links
        for _ in range(NUMBER_PAGES):
            for pedido in self.driver.find_elements(By.CLASS_NAME, "ms-srch-ellipsis"):
                links = pedido.find_elements(By.TAG_NAME, "a")
                for link in links:
                    caso = link.get_attribute("href")
                    list_of_links.append(caso)
            # click on the next page
            try:
                self.driver.find_element(By.XPATH, '//*[@id="PageLinkNext"]').click()
                time.sleep(2)
            except:
                break
        logger.info(f"Found {len(list_of_links)} requests")
        return list_of_links

    def store_requests(self, list_of_links: List[str]) -> List[Dict]:
        """store the request information as a list of dictionaries

        Parameters
        ----------
        list_of_links : List[str]
            [description]

        Returns
        -------
        List
            List of dictionaries containing the link, text and summary of requests
        """
        request_list = []
        for link in list_of_links:
            temp_dict = {}
            self.driver.get(link)
            resumao = self.driver.find_element(
                By.XPATH,
                "/html/body/form/div[4]/div[10]/div[1]/div[2]/div/div[2]/div[2]/div[1]/table/tbody/tr/td/div/div[3]/div[1]/div/div[1]/span/div[2]/div/div[2]/div/div/div/div[2]/div[1]/div/div/fieldset/div/div[1]/span/textarea",
            )
            temp_dict["resumo"] = resumao.text
            link_do_pedido = self.driver.find_element(
                By.XPATH,
                "/html/body/form/div[4]/div[10]/div[1]/div[2]/div/div[2]/div[2]/div[1]/table/tbody/tr/td/div/div[3]/div[1]/div/div[1]/span/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/div/fieldset/div/div[3]/table/tbody/tr/td[2]/div/span/textarea",
            )
            temp_dict["link"] = link_do_pedido.text
            texto_do_pedido = self.driver.find_element(
                By.XPATH,
                "/html/body/form/div[4]/div[10]/div[1]/div[2]/div/div[2]/div[2]/div[1]/table/tbody/tr/td/div/div[3]/div[1]/div/div[1]/span/div[2]/div/div[2]/div/div/div/div[2]/div[4]/div/div/fieldset/div/div/table/tbody/tr/td[2]/div[1]/span/div",
            )
            temp_dict["texto_do_pedido"] = texto_do_pedido.text
            request_list.append(temp_dict)

        return request_list

    def export_dataframe(self, request_list: List[Dict], export_path: str):

        df = pd.DataFrame(request_list)
        logger.info(
            f"Exporting {df.shape[0]} requests from the last {self.number_days} days"
        )
        df.to_csv(export_path)
