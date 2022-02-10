from scraper import Scraper
from argparse import ArgumentParser


def main(args):
    web_scraper = Scraper()
    web_scraper.load_initial_page(args.number_days, args.keyword)
    list_of_links = web_scraper.search_requests()
    requests_list = web_scraper.store_requests(list_of_links)
    web_scraper.export_dataframe(requests_list, args.export_path)


if __name__ == "__main__":

    parser = ArgumentParser(description="Input parameters")
    parser.add_argument("--keyword", "-k", type=str, help="keyword to be searched")
    parser.add_argument(
        "--number_days",
        "-n",
        type=int,
        default=30,
        help="number of days to look back for requests",
    )
    parser.add_argument("--export_path", "-o", type=str, help="output path")

    args = parser.parse_args()

    main(args)
