# Solving Open Shop Job Scheduling Problem using Z3

Solving gp03-01 instances using Z3.

## SAT Ver.

```sh
poetry run python ./src/main.py
```

## SMT Ver.

```sh
poetry run python ./src/smt.py
```

## References

- [人工知能 2010年25巻1号](https://www.jstage.jst.go.jp/browse/jjsai/25/1/_contents/-char/ja)
  - [SATによるプランニングとスケジューリング](https://www.jstage.jst.go.jp/article/jjsai/25/1/25_114/_article/-char/ja/)
- [ショップ・スケジューリング問題の SAT 変換による解法](https://tamura70.gitlab.io/papers/pdf/ss07t.pdf)
- [Experimental Results on the Application of Satisfiability Algorithms to Scheduling Problems - AAAI](https://aaai.org/papers/01092-aaai94-168-experimental-results-on-the-application-of-satisfiability-algorithms-to-scheduling-problems/)
- [Survey for Open Shop Scheduling](https://jqcsm.qu.edu.iq/index.php/journalcm/article/view/1965)
