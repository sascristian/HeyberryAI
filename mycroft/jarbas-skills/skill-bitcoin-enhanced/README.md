# mycroft-skill-bitcoin-enhanced
A skill for MycroftAI that querys various bitcoin statistics.

## DESCRIPTION:

This Mycroft skill is an enhancement of the bitcoin-skill by Red5d.
(https://github.com/Red5d/mycroft_skills/tree/master/bitcoin)

The bitcoin statistics are obtained from bitcoinaverage.com.
(https://api.bitcoinaverage.com/all)

The original skill assumes the currency is  US dollars (USD) and
only provided the 24-hour average price.  I have expanded the
statistics to include all of the following:

- Asking Price
- Bid Price
- Last Price
- 24-hour Average Price
- Volume (in BTC)

As well, I have created a regex that distinguishes between the 
currencies available at bitcoinaverage.  The current list of 
available currencies is as follows:

- Brazilian Reals (BRL)
- British Pounds (GBP)
- Canadian Dollars (CAD)
- Euros (EUR)
- Chinese Yuans (CNY)
- Czech Koruna (CZK)
- Indonesian Rupiahs (IDR)
- Israeli shekels (ILS)
- Indian Rupees (INR)
- Japanese Yens (JPY)
- South Korean Won (KRW)
- Mexican Pesos (MXN)
- Malaysian Ringgit (MYR)
- Nigerian Nairas (NGN)
- Polish Zlotys:  (PLN)
- Russian Roubles (RUB)
- Swedish Kronas (SEK)
- Singapore Dollars (SGD)
- Turkish Lira (TRY)
- US Dollars (USD)
- South African Rands (ZAR)

###### NOTE:

For most currencies use the currency's short name (e.g. "Euros" or
"Shekels").  However, this does not work when the currency's name is
"dollars" because there are multiple currencies with that name.  In
those cases you *must* use the full name (e.g. "Canadian Dollars" or
"Singapore Dollars").  In the case of US dollars you can use either
"American Dollars" or "USA Dollars."  If no currency is specified
"USD" is used.

## USAGE:

###### Asking Price

Say any phrase that contains one of the following keywords:

- high bitcoin price
- highest bitcoin price
- asking bitcoin price
- bitcoin ask price
- bitcoin asking price

*(Example:  "What is the asking bitcoin price in Euros?")*

###### Bid Price

Say any phrase that contains one of the following keywords:

- low bitcoin price
- lowest bitcoin price
- bitcoin bid price

*(Example:  "Tell me the bitcoin bid price.")*

###### Last Price

Say any phrase that contains one of the following keywords:

- bitcoin price
- last bitcoin price
- bitcoin last price
- current bitcoin price

*(Example:  "What in Pesos is the last bitcoin price?)*

###### 24-hour Average Price

Say any phrase that contains one of the following keywords:

- average bitcoin price
- bitcoin average price

*(Example:  "Tell me the average bitcoin price in Yuan.)*

###### 24-hour Volume

Say any phrase that contains one of the following keywords:

- bitcoin volume
- volume of bitcoin

*(Example:  "What is the volume of bitcoin in Zlotys?)*

## TODO:

1.  This is the initial version of this skill and I have only done
preliminary debugging of the code.  I would welcome people testing the skill
and letting me know of any problems/bugs at chrison999 (at) yahoo.ca. 
Please put "Mycroft Bitcoin Skill" in the subject of your message.

2.  Bitcoinaverage.com has a lot more statistics available such has
statistics for exchanges selling bitcoin in each currency.  Possible future
enhancements could include:
    - Reporting which exchanges sell bitcoin in each currency *(e.g. "What are
the bitcoin exchanges for Euros?")*
    - Reporting statistic for an exchange *(e.g. "What is the last price for
bitcoin in Euros for Bitonic?")*
