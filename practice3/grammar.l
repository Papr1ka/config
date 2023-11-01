%option noyywrap yylineno
%{
#include <stdio.h>
#include "y.tab.h"
int state;
void UndefinedTokenPrint();
int lexInOpen(char* filename);
void lexInClose();
int number;
%}

LETTER [a-zA-Z]
DIGIT [0-9]
IDENTIFIER {LETTER}({LETTER}|{DIGIT})*
STRING \"([^\"]*)?\"
NUMBER {DIGIT}+
COMMENT \/\*.*\*\/
SEPARATOR_PLUS \+
SEPARATOR_MINUS -
SEPARATOR_MUL \*
SEPARATOR_DIV \/
SEPARATOR_GT >
SEPARATOR_LT <
SEPARATOR_LB \(
SEPARATOR_RB \)
KEYWORD_CALC calc
KEYWORD_LIST list
KEYWORD_VAR var
KEYWORD_PUSH push
KEYWORD_WHILE while
KEYWORD_DEFINE define
KEYWORD_RETURN return
KEYWORD_CALL call
KEYWORD_OBJECT object

DELIM [ \t\n]

%%
{DELIM} {;}
{KEYWORD_WHILE} {  printf("Lex: %s\n", yytext); return KEYWORD_WHILE; }
{KEYWORD_OBJECT} {   printf("Lex: %s\n", yytext); return KEYWORD_OBJECT; }
{KEYWORD_CALL} {   printf("Lex: %s\n", yytext);return KEYWORD_CALL; }
{KEYWORD_RETURN} {   printf("Lex: %s\n", yytext);return KEYWORD_RETURN; }
{KEYWORD_DEFINE} {   printf("Lex: %s\n", yytext);return KEYWORD_DEFINE; }
{KEYWORD_CALC} {   printf("Lex: %s\n", yytext);return KEYWORD_CALC; }
{KEYWORD_LIST} {   printf("Lex: %s\n", yytext);return KEYWORD_LIST; }
{KEYWORD_VAR} {   printf("Lex: %s\n", yytext);return KEYWORD_VAR; }
{KEYWORD_PUSH} {   printf("Lex: %s\n", yytext);return KEYWORD_PUSH; }
{SEPARATOR_PLUS} {  printf("Lex: %s\n", yytext);return SEPARATOR_PLUS; }
{SEPARATOR_MINUS} {   printf("Lex: %s\n", yytext);return SEPARATOR_MINUS; }
{SEPARATOR_MUL} {   printf("Lex: %s\n", yytext);return SEPARATOR_MUL; }
{SEPARATOR_DIV} {  printf("Lex: %s\n", yytext);return SEPARATOR_DIV; }
{SEPARATOR_GT} {  printf("Lex: %s\n", yytext);return SEPARATOR_GT; }
{SEPARATOR_LT} {  printf("Lex: %s\n", yytext);return SEPARATOR_LT; }
{SEPARATOR_LB} {  printf("Lex: %s\n", yytext);return SEPARATOR_LB; }
{SEPARATOR_RB} {  printf("Lex: %s\n", yytext);return SEPARATOR_RB; }
{NUMBER} {   printf("Lex: %s\n", yytext);yylval.number_value = atoi(yytext); return (NUMBER); }
{IDENTIFIER} {   printf("Lex: %s\n", yytext);strcpy(yylval.name, yytext); return (IDENTIFIER); }
{STRING} {  printf("Lex: %s\n", yytext);strcpy(yylval.name, yytext); return (STRING); }
{COMMENT} {;}
%%

int lexInOpen(char* filename)
{
	if((yyin = fopen(filename, "r")) == NULL)
	{
		
		return -1;
	}
	yylineno = 1;
    return 0;
}

void lexInClose()
{
    fclose(yyin);
}

void UndefinedTokenPrint()
{
	
}