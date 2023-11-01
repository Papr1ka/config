#ifndef _yy_defines_h_
#define _yy_defines_h_

#define IDENTIFIER 257
#define STRING 258
#define NUMBER 259
#define SEPARATOR_PLUS 260
#define SEPARATOR_MINUS 261
#define SEPARATOR_MUL 262
#define SEPARATOR_DIV 263
#define SEPARATOR_GT 264
#define SEPARATOR_LT 265
#define SEPARATOR_LB 266
#define SEPARATOR_RB 267
#define KEYWORD_CALC 268
#define KEYWORD_LIST 269
#define KEYWORD_VAR 270
#define KEYWORD_PUSH 271
#define KEYWORD_WHILE 272
#define KEYWORD_DEFINE 273
#define KEYWORD_RETURN 274
#ifdef YYSTYPE
#undef  YYSTYPE_IS_DECLARED
#define YYSTYPE_IS_DECLARED 1
#endif
#ifndef YYSTYPE_IS_DECLARED
#define YYSTYPE_IS_DECLARED 1
typedef union YYSTYPE{
    char name[100];
} YYSTYPE;
#endif /* !YYSTYPE_IS_DECLARED */
extern YYSTYPE yylval;

#endif /* _yy_defines_h_ */
