# exam_generator

Python companion for exam documentclass that creates multiple exam versions from question banks.

## Usage

### Installation
```bash
pip install pyyaml
```

### Example Usage

```bash
python exam_generator.py exam_config.yaml --versions 3 --output-dir exams/
```

### Command Line Options

- `exam_config.yaml`: Required. Configuration file specifying question banks and selection criteria
- `--versions`: Number of exam versions to generate (default: 1)
- `--output-dir`: Directory for output files (default: current directory)
- `--preamble`: Custom LaTeX preamble file
- `--no-shuffle`: Disable shuffling of answer choices

### Files

#### Question Bank

```yaml
name: basic_c
questions:
  - id: q1
    type: multiple_choice
    points: 3
    text: |
      What is the time complexity?

      \begin{verbatim}
      int binary_search(int arr[], int n, int x) {
          int left = 0, right = n - 1;
          while (left <= right) {
              int mid = left + (right - left) / 2;
              if (arr[mid] == x) return mid;
              if (arr[mid] < x) left = mid + 1;
              else right = mid - 1;
          }
          return -1;
      }
      \end{verbatim}
    choices:
      - O(n)
      - O(log n)
      - O(n log n)
      - O(1)
    correct_answers: O(log n)

  - id: q2
    type: multiple_selection
    points: 3
    text: Which of the following are valid ways to declare a pointer in C?
    verbatim_choices: true
    choices:
      - |
        int* ptr;
      - |
        int *ptr;
      - |
        int (* ptr);
      - |
        ptr* int;
    correct_answers:
      - |
        int* ptr;
      - |
        int *ptr;
```

#### Configuration File

```yaml
question_banks:
  - bits.yaml
  - floating_point.yaml
  - basic_c.yaml

selections:
  bits: 2
  floating_point: 3
  basic_c: 2
```
