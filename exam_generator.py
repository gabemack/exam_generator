import yaml
import random
from pathlib import Path
from typing import Dict, List, Any
import argparse
from datetime import datetime

class Question:
    def __init__(self, data: Dict[str, Any]):
        self.text = data['text']
        self.points = data.get('points', 1)
        self.type = data['type']  # 'multiple_choice' or 'multiple_selection'
        self.choices = data['choices']
        self.correct_answers = data['correct_answers']
        self.id = data.get('id', '')
        self._shuffled_indices = None

    def shuffle_choices(self):
        """Shuffle the choices"""
        n = len(self.choices)
        self._shuffled_indices = list(range(n))
        random.shuffle(self._shuffled_indices)

    def get_shuffled_choices(self):
        if self._shuffled_indices is None:
            self.shuffle_choices()

        shuffled_choices = [self.choices[i] for i in self._shuffled_indices]

        if isinstance(self.correct_answers, list):
            # Track the correct answers for multiple selection
            shuffled_correct = []
            for i, choice in enumerate(shuffled_choices):
                if choice in self.correct_answers:
                    shuffled_correct.append(choice)
            return shuffled_choices, shuffled_correct
        else:
            # Multiple choice
            return shuffled_choices, self.correct_answers

    def to_latex(self, shuffle: bool = True) -> str:
        # Convert question to latex format
        latex = f"\\question[{self.points}] {self.text}\n"
        latex += "\\begin{choices}\n"

        if shuffle:
            choices, correct = self.get_shuffled_choices()
        else:
            choices = self.choices
            correct = self.correct_answers

        for choice in choices:
            if isinstance(correct, list):
                # Multiple selection
                if choice in correct:
                    latex += f"\\correctchoice {choice}\n"
                else:
                    latex += f"\\choice {choice}\n"
            else:
                # Multiple choice
                if choice == correct:
                    latex += f"\\correctchoice {choice}\n"
                else:
                    latex += f"\\choice {choice}\n"

        latex += "\\end{choices}\n"
        return latex

class QuestionBank:
    def __init__(self, yaml_file: str):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self.name = data['name']
        self.questions = [Question(q) for q in data['questions']]

    def sample_questions(self, n: int) -> List[Question]:
        """Randomly sample n questions from the bank"""
        if n > len(self.questions):
            raise ValueError(f"Requested {n} questions but bank only has {len(self.questions)}")
        return random.sample(self.questions, n)

class ExamGenerator:
    def __init__(self, preamble_file: str = None):
        self.banks: Dict[str, QuestionBank] = {}
        self.preamble_file = preamble_file

    def add_bank(self, yaml_file: str):
        bank = QuestionBank(yaml_file)
        self.banks[bank.name] = bank

    def generate_exam(self, bank_selections: Dict[str, int], version: int) -> str:
        """Generate a single exam version"""
        latex = self._generate_preamble(version)

        # Sample questions from each bank
        all_questions = []
        for bank_name, num_questions in bank_selections.items():
            if bank_name not in self.banks:
                raise ValueError(f"Question bank '{bank_name}' not found")
            questions = self.banks[bank_name].sample_questions(num_questions)
            all_questions.extend(questions)

        # Generate questions in LaTeX
        latex += "\\begin{questions}\n"
        for question in all_questions:
            latex += question.to_latex() + "\n"
        latex += "\\end{questions}\n"

        latex += "\\end{document}"
        return latex

    def _generate_preamble(self, version: int) -> str:
        """Generate latex preamble"""
        if self.preamble_file:
            try:
                with open(self.preamble_file, 'r', encoding='utf-8') as f:
                    preamble = f.read()
                # Replace placeholder for version number if it exists
                preamble = preamble.replace('%%VERSION%%', str(version))
                return preamble
            except FileNotFoundError:
                print(f"Warning: Preamble file {self.preamble_file} not found. Using default preamble.")

        # Default preamble
        return f"""\\documentclass[addpoints,12pt,answers]{{exam}}
\\usepackage{{ttfamily}}
\\usepackage{{textcomp}}
\\pagestyle{{headandfoot}}
\\runningheader{{CS Course}}{{Exam Version {version}}}{{\\today}}
\\runningfooter{{Page \\thepage\\ of \\numpages}}{{}}{{}}

\\begin{{document}}
\\begin{{center}}
\\textbf{{Exam}}\\\\
Version {version}\\\\
\\today
\\end{{center}}

"""

def main():
    parser = argparse.ArgumentParser(description='Generate multiple versions of an exam')
    parser.add_argument('config', help='YAML config file with bank selections')
    parser.add_argument('--versions', type=int, default=1, help='Number of versions to generate')
    parser.add_argument('--output-dir', type=Path, default=Path('.'), help='Output directory')
    parser.add_argument('--preamble', help='Custom LaTeX preamble file')
    parser.add_argument('--no-shuffle', action='store_true', help='Disable shuffling of answer choices')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    generator = ExamGenerator(preamble_file=args.preamble)
    for bank_file in config['question_banks']:
        generator.add_bank(bank_file)

    args.output_dir.mkdir(exist_ok=True)

    for version in range(1, args.versions + 1):
        latex = generator.generate_exam(config['selections'], version)
        output_file = args.output_dir / f"exam_v{version}.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex)

if __name__ == "__main__":
    main()
