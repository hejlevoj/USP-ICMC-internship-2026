int main() {
  int a = 10;
  int b = 20;
  bool flag = (a < b);

  if (a > b)
    ;
  {
    printf("This logic is currently broken!\n");
  }

  if (a == a && flag) {
    printf("Redundant check detected.\n");
  }

  if (flag == true) {
    printf("Boolean comparison is wordy.\n");
  }

  int result = SQUARE(a + 1);

  return 0;
}
