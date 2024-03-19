# Coding test for y-intercept

## Strategies
* SMA
* Standard MACD
* Adaptive MACD
Resulted trades are plotted against technical indicators in their respective `html` files.

## Results
### SMA
Out of my expectation, SMA performs the best. Chart: `SMAStrat.html`.
```
        Strat Return Hold Return
1332 JT   260.930188   67.366399
1333 JT   -12.206747    2.105676
1334 JT          0.0         0.0
1605 JT   102.339721  159.206012
1721 JT   -19.954719   72.365499
...              ...         ...
9735 JT   -45.321116   57.313891
9766 JT     0.660555   95.121482
9843 JT    -2.226807   52.455438
9983 JT   -48.635996  333.549861
9984 JT    -52.56268  112.152002

Average SMA return: 14.398205129277562
Average hold return: 108.97037936623173
```

Parameter optimization is conducted on "1332 JT". It seems that (11,20) is the best combination for this particular stock. Further optimization can be done with the whole portfolio.
However, the unbelievable phenomenum is that return of SMA strategy is worse than buy-and-hold -- maybe this portfolio is a very good one (hopefully this is the portfolio y-intercept is holding XD).

### Adaptive MACD
Sadly, the more complicated strategy among the three implemeted today is the worst performer.
```
        Strat Return Hold Return
1332 JT    53.119731   67.366399
1333 JT     4.210958    2.105676
1334 JT          0.0         0.0
1605 JT     28.40869  159.206012
1721 JT   -32.578795   72.365499
...              ...         ...
9735 JT     6.812675   57.313891
9766 JT   -54.551241   95.121482
9843 JT     4.677604   52.455438
9983 JT   -47.220783  333.549861
9984 JT   -51.396907  112.152002

[263 rows x 2 columns]
Average Adaptive MACD return: 7.58135280988594
Average hold return: 108.97037936623173
```
Sorry but I really don't have time to dig deeper into these parameters today. I may be able to play with the numbers during the coming weekend.
