# solidabis-koodihaaste
Projekti on toteutettu Python kielellä ja käyttämällä flaskia pyörittämään web palvelinta. Pythonin json kirjastoa on myös käytetty .json tiedoston tulkintaan.
Pystyy nakemään projektin osoiteesta https://solidabis-koodihaaste.herokuapp.com/ tai voi käynistää pythonin virtual environmentissa omassa koneessa:
1. Asenna python koneeseen
2. Muokkaa main.py tiedostossa viivaa 150 "app.run(host='0.0.0.0', port=port)" muotoon "app.run()"
3. Anna cmd käskyt projekti kansiossa (windows käskyt):
	1. "py -m pip install virtualenv"
	2. "py -3 -m venv venv"
	3. "venv\Scripts\activate"
	4. "pip install Flask"
	5. käynistä käskyllä "py main.py"
4. Projektia sitten pystyy katsomaan osoiteesta 127.0.0.1:5000

Ongelma on ratkaistu tulkitsemalla json tiedostoa pythonin json kirjastolla josta tieto on tallennettu Stop classeihin.
Jokainen Stop class sisältää yhden pysäkin nimen, pysäkin yhteydet (linjasto yhteydet ei tie yhteydet), ja yhteyksien kesto. Nämä Stop classit pystyvät tarkistamaan onko niilä yhteys tiettyyn pysäkkiin tai jos ei ole pystyy kysymään yhteksiltä onko niilä yhteys kyseiseen pysäkkiin tai jos ei ole ne kysyy omilta yhteyksiltä onko niilä yhteys ja niin edeleen kunnes se pysäkki löytyy.
Kun pysäkki löytyy sen aika ja mitä pysäkkejä käytettiin lähetetään edelliselle pysäkille joka vertaa tuloksia ja lähettää takaisin vain lyhkäisimmän reitin. Jokainen pysäkki tekee näin kunnes tieto palaa alkuperäiselle pysäkille joka palauttaa kaiken parhaimman reitin.
Lopuksi ohjelma rakentaa string vastauksen ja palauttaa sen sivustolle.

Huomioitavaa ohjelmassa on että se olettaa .json tiedoston olevan ehjänä ja pysäkkien olevan A-Z. Myös on oletettu että linjat kulkevat molempiin suuntiin vaikka ei erikseen mainittu, koska käytännössä ne yleensä kulkee niin. Tämä ratkaisu ei skaalaa hyvin kun on monta pysäkkiä, mutta tämnöiseen käyttöön on sopiva.
