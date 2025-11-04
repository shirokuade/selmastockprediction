"""
Top 100 most popular Indonesian stocks (IDX)
Based on market capitalization and trading volume
"""

TOP_100_INDONESIAN_STOCKS = [
    # Banking
    {"symbol": "BBCA", "name": "Bank Central Asia", "sector": "Banking"},
    {"symbol": "BMRI", "name": "Bank Mandiri", "sector": "Banking"},
    {"symbol": "BBRI", "name": "Bank Rakyat Indonesia", "sector": "Banking"},
    {"symbol": "BBNI", "name": "Bank Negara Indonesia", "sector": "Banking"},
    {"symbol": "BBTN", "name": "Bank Tabungan Negara", "sector": "Banking"},
    {"symbol": "BRIS", "name": "Bank BRI Syariah", "sector": "Banking"},
    {"symbol": "BJBR", "name": "Bank Pembangunan Daerah Jawa Barat", "sector": "Banking"},
    {"symbol": "MEGA", "name": "Bank Mega", "sector": "Banking"},
    {"symbol": "PNBN", "name": "Bank Pan Indonesia", "sector": "Banking"},
    {"symbol": "NISP", "name": "Bank OCBC NISP", "sector": "Banking"},

    # Telecommunication
    {"symbol": "TLKM", "name": "Telkom Indonesia", "sector": "Telecommunication"},
    {"symbol": "EXCL", "name": "XL Axiata", "sector": "Telecommunication"},
    {"symbol": "ISAT", "name": "Indosat Ooredoo", "sector": "Telecommunication"},

    # Consumer Goods
    {"symbol": "UNVR", "name": "Unilever Indonesia", "sector": "Consumer Goods"},
    {"symbol": "HMSP", "name": "HM Sampoerna", "sector": "Consumer Goods"},
    {"symbol": "ICBP", "name": "Indofood CBP", "sector": "Consumer Goods"},
    {"symbol": "INDF", "name": "Indofood Sukses Makmur", "sector": "Consumer Goods"},
    {"symbol": "KLBF", "name": "Kalbe Farma", "sector": "Consumer Goods"},
    {"symbol": "MYOR", "name": "Mayora Indah", "sector": "Consumer Goods"},
    {"symbol": "ULTJ", "name": "Ultra Jaya Milk", "sector": "Consumer Goods"},
    {"symbol": "DVLA", "name": "Darya-Varia Laboratoria", "sector": "Consumer Goods"},
    {"symbol": "TSPC", "name": "Tempo Scan Pacific", "sector": "Consumer Goods"},
    {"symbol": "KAEF", "name": "Kimia Farma", "sector": "Consumer Goods"},
    {"symbol": "SIDO", "name": "Industri Jamu Sido Muncul", "sector": "Consumer Goods"},

    # Automotive
    {"symbol": "ASII", "name": "Astra International", "sector": "Automotive"},
    {"symbol": "AUTO", "name": "Astra Otoparts", "sector": "Automotive"},
    {"symbol": "GJTL", "name": "Gajah Tunggal", "sector": "Automotive"},
    {"symbol": "IMAS", "name": "Indomobil Sukses International", "sector": "Automotive"},

    # Property & Real Estate
    {"symbol": "BSDE", "name": "Bumi Serpong Damai", "sector": "Property"},
    {"symbol": "CTRA", "name": "Ciputra Development", "sector": "Property"},
    {"symbol": "PWON", "name": "Pakuwon Jati", "sector": "Property"},
    {"symbol": "SMRA", "name": "Summarecon Agung", "sector": "Property"},
    {"symbol": "APLN", "name": "Agung Podomoro Land", "sector": "Property"},
    {"symbol": "DILD", "name": "Intiland Development", "sector": "Property"},

    # Mining
    {"symbol": "ADRO", "name": "Adaro Energy", "sector": "Mining"},
    {"symbol": "PTBA", "name": "Bukit Asam", "sector": "Mining"},
    {"symbol": "INCO", "name": "Vale Indonesia", "sector": "Mining"},
    {"symbol": "ANTM", "name": "Aneka Tambang", "sector": "Mining"},
    {"symbol": "TINS", "name": "Timah", "sector": "Mining"},
    {"symbol": "ITMG", "name": "Indo Tambangraya Megah", "sector": "Mining"},
    {"symbol": "MEDC", "name": "Medco Energi International", "sector": "Mining"},
    {"symbol": "BYAN", "name": "Bayan Resources", "sector": "Mining"},
    {"symbol": "HRUM", "name": "Harum Energy", "sector": "Mining"},

    # Cement
    {"symbol": "SMGR", "name": "Semen Indonesia", "sector": "Cement"},
    {"symbol": "INTP", "name": "Indocement Tunggal Prakarsa", "sector": "Cement"},
    {"symbol": "WTON", "name": "Wijaya Karya Beton", "sector": "Cement"},

    # Retail
    {"symbol": "ACES", "name": "Ace Hardware Indonesia", "sector": "Retail"},
    {"symbol": "MAPI", "name": "Mitra Adiperkasa", "sector": "Retail"},
    {"symbol": "RALS", "name": "Ramayana Lestari Sentosa", "sector": "Retail"},
    {"symbol": "MPPA", "name": "Matahari Putra Prima", "sector": "Retail"},

    # Technology & Media
    {"symbol": "GOTO", "name": "GoTo Gojek Tokopedia", "sector": "Technology"},
    {"symbol": "BUKA", "name": "Bukalapak.com", "sector": "Technology"},
    {"symbol": "EMTK", "name": "Elang Mahkota Teknologi", "sector": "Media"},
    {"symbol": "SCMA", "name": "Surya Citra Media", "sector": "Media"},

    # Energy
    {"symbol": "PGAS", "name": "Perusahaan Gas Negara", "sector": "Energy"},
    {"symbol": "ELSA", "name": "Elnusa", "sector": "Energy"},

    # Construction
    {"symbol": "WIKA", "name": "Wijaya Karya", "sector": "Construction"},
    {"symbol": "WSKT", "name": "Waskita Karya", "sector": "Construction"},
    {"symbol": "PTPP", "name": "PP Persero", "sector": "Construction"},
    {"symbol": "ADHI", "name": "Adhi Karya", "sector": "Construction"},
    {"symbol": "TOTL", "name": "Total Bangun Persada", "sector": "Construction"},

    # Transportation
    {"symbol": "GIAA", "name": "Garuda Indonesia", "sector": "Transportation"},
    {"symbol": "JSMR", "name": "Jasa Marga", "sector": "Transportation"},

    # Agriculture
    {"symbol": "AALI", "name": "Astra Agro Lestari", "sector": "Agriculture"},
    {"symbol": "LSIP", "name": "PP London Sumatra Indonesia", "sector": "Agriculture"},
    {"symbol": "SGRO", "name": "Sampoerna Agro", "sector": "Agriculture"},
    {"symbol": "SIMP", "name": "Salim Ivomas Pratama", "sector": "Agriculture"},

    # Electronics
    {"symbol": "KBLV", "name": "First Media", "sector": "Electronics"},
    {"symbol": "LINK", "name": "Link Net", "sector": "Electronics"},

    # Paper & Pulp
    {"symbol": "INKP", "name": "Indah Kiat Pulp & Paper", "sector": "Paper"},
    {"symbol": "TKIM", "name": "Pabrik Kertas Tjiwi Kimia", "sector": "Paper"},

    # Plastic & Packaging
    {"symbol": "TPIA", "name": "Chandra Asri Petrochemical", "sector": "Plastic"},
    {"symbol": "AKPI", "name": "Argha Karya Prima Industry", "sector": "Plastic"},
    {"symbol": "APLI", "name": "Asiaplast Industries", "sector": "Plastic"},

    # Steel
    {"symbol": "JPFA", "name": "Japfa Comfeed Indonesia", "sector": "Agriculture"},
    {"symbol": "MAIN", "name": "Malindo Feedmill", "sector": "Agriculture"},

    # Hotels & Tourism
    {"symbol": "PANS", "name": "Panin Sekuritas", "sector": "Finance"},
    {"symbol": "HATM", "name": "Hotel Mandarine Regency", "sector": "Hotels"},

    # Healthcare
    {"symbol": "HEAL", "name": "Medikaloka Hermina", "sector": "Healthcare"},
    {"symbol": "SILO", "name": "Siloam International Hospitals", "sector": "Healthcare"},
    {"symbol": "MIKA", "name": "Mitra Keluarga Karyasehat", "sector": "Healthcare"},

    # Investment
    {"symbol": "BFIN", "name": "BFI Finance Indonesia", "sector": "Finance"},
    {"symbol": "ADMF", "name": "Adira Dinamika Multi Finance", "sector": "Finance"},

    # Additional Blue Chips
    {"symbol": "GGRM", "name": "Gudang Garam", "sector": "Consumer Goods"},
    {"symbol": "UNTR", "name": "United Tractors", "sector": "Heavy Equipment"},
    {"symbol": "BRPT", "name": "Barito Pacific", "sector": "Petrochemical"},
    {"symbol": "ERAA", "name": "Erajaya Swasembada", "sector": "Retail"},
    {"symbol": "ESSA", "name": "Surya Esa Perkasa", "sector": "Retail"},
    {"symbol": "HRTA", "name": "Hartadinata Abadi", "sector": "Retail"},
    {"symbol": "SRTG", "name": "Saratoga Investama Sedaya", "sector": "Investment"},
    {"symbol": "TOWR", "name": "Sarana Menara Nusantara", "sector": "Telecommunication"},
    {"symbol": "TBIG", "name": "Tower Bersama Infrastructure", "sector": "Telecommunication"},
    {"symbol": "MDKA", "name": "Merdeka Copper Gold", "sector": "Mining"},
]


def get_top_100_stocks():
    """Get list of top 100 stocks with rank"""
    return [
        {**stock, "rank": idx + 1}
        for idx, stock in enumerate(TOP_100_INDONESIAN_STOCKS)
    ]


def get_stock_symbols():
    """Get just the symbols"""
    return [stock["symbol"] for stock in TOP_100_INDONESIAN_STOCKS]


if __name__ == "__main__":
    print(f"Total stocks: {len(TOP_100_INDONESIAN_STOCKS)}")
    print(f"Symbols: {get_stock_symbols()}")
