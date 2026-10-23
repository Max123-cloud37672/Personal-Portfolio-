# Development log

A record of what was built, the decisions made, the bugs I hit and what I learned.

## Friday 23 October 2026

### What was built

| Milestone | Pull request |
|---|---|
| Project setup: virtual environment, pinned dependencies, pytest and Ruff settings | #1 |
| `Holding` class with gain/loss calculations and validation (after renaming the package) | #2 |
| GitHub Actions CI running Ruff and pytest on every pull request | #3 |
| First README | #4 |
| `Portfolio` class: totals, weights, allocation by sector and asset type | #5 |
| CSV loader and illustrative data for three fictional clients | #6 |
| Streamlit dashboard | #7 |

### Decisions

- **Changed the project's direction.** I started planning a fixed-income
  analytics dashboard (bond pricing, yield to maturity, duration). After the
  setup milestone I decided it was too much to understand properly before my
  deadline, and narrowed it to a stock and ETF portfolio tracker for
  high-net-worth clients. A smaller project I can fully explain is better than a
  bigger one I can't.
- **Fictional clients only.** Real client data is confidential, so all three
  clients are labelled "Client A/B/C" and every price is made up.
- **Canadian-listed holdings in CAD only,** so there is no currency conversion
  yet. US holdings are a possible next step.
- **Prices in their own file** (`prices.csv`), separate from client positions
  (`holdings.csv`), so each security has a single price shared by every client.
- **Tests before code** for every feature (red, then green, then refactor).
- **One branch and one pull request per milestone,** so `main` only ever
  contains finished, tested work.

### Bugs and problems, and how they were fixed

| Problem | Cause | Fix |
|---|---|---|
| `zsh: command not found: python` | Typed `python 3.13` (with a space, and the wrong version) | The command is `python3.14`, with no space |
| Terminal stuck at `dquote>` | A commit message was missing its closing `"` | Ctrl + C to cancel, then paste the command again |
| Terminal turned into a full-screen viewer after `git diff --staged` | Git opens long output in a "pager" | Press `q` to quit |
| Commits showed `maxobadia@mac.home` | Git's name and email were never set, so it guessed | `git config --global user.name` and `user.email` |
| `pathspec ... did not match any files` | Typed `portfolio` instead of `portfolio.py` | Copy and paste paths, or stage whole folders (`git add src tests`) |
| `error: unknown switch ','` | Typed `-,` instead of `-m` in `git commit` | Retype the command with `-m` |
| `AttributeError: 'Portfolio' object has no attribute 'number_of_holdings'` | The test ran before the property existed (expected: the red step) | Wrote the property |
| `assert None == 4` | My first version had no `return` line, and `"return_"` in quotes is just text | `return len(self.holdings)` |
| `name 'Holdings' is not defined` | Python is case-sensitive: the variable is `holdings`; only the label text is `"Holdings"` | Lowercase variable, capitalised label |
| Browser said `localhost:8501` can't be reached | Streamlit was still waiting at its first-run "Email:" question | Press Enter in the terminal |
| My GitHub repository returned "not found" to anyone logged out | The repository is private | Make it public before sharing |

### What I learned

- **Git and GitHub:** Saving work takes two steps: `git add` picks what goes in,
  and `git commit` saves it with a message. Pushing sends it to GitHub. I worked
  on a separate branch for each milestone and merged it into `main` through a
  pull request, so `main` only ever had finished work. I also learned to stage
  only some files, so one branch could have a "refactor" commit and a "feature"
  commit kept separate.
- **Testing:** You write the test first and watch it fail, so you know it is
  really checking something. The type of error tells you what is wrong: an
  `AttributeError` means the thing doesn't exist yet, while an `AssertionError`
  means it exists but gives the wrong answer. One typo can make several tests
  fail at once if it crashes the page they all depend on.
- **Python:** A class is a blueprint, and each holding is an object made from
  it. The `-> int` part says what *type* of answer comes back, and `return`
  gives the actual answer. Without a `return` line a function gives back
  `None`. Python is case-sensitive, and text in quotes is just text. A file
  name or folder path is not a command you can type in the terminal.
- **Finance:** Cost basis is what the client paid, and market value is what the
  holdings are worth today. Gain/loss is the difference between them. Weights
  and allocation use market value, because they describe what the client owns
  now. The portfolio's total gain/loss % is total gain divided by total cost,
  not an average of each holding's percentage.
- **Working with an AI assistant:** It wrote code quickly and explained it
  clearly, but that is not the same as me understanding it. When I realised I
  had not written any of the code myself, I asked to start writing parts of it.
  Even small pieces (one property, one line on the dashboard, eight rows of
  data) taught me more than reading explanations did. Next time I would write
  more of the code myself from the start.
