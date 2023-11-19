%option noyywrap
%option yylineno

%{
#include <stdio.h>
#include "sson.tab.h"
int state;
void UndefinedTokenPrint();
int lexInOpen(char* filename);
void lexInClose();

extern int tabs;
%}

LETTER [a-zA-Z]
DIGIT [0-9]
IDENTIFIER {LETTER}({LETTER}|{DIGIT})*
STRING \"([^\"]*)?\"
NUMBER {DIGIT}+
COMMENT \/\*.*\*\/
SEPARATOR_LB \(
SEPARATOR_RB \)
KEYWORD_LIST list

DELIM [ \t\n]

%%
{DELIM} {;}
{KEYWORD_LIST} { return KEYWORD_LIST; }
{SEPARATOR_LB} { tabs++; return SEPARATOR_LB; }
{SEPARATOR_RB} { tabs--; return SEPARATOR_RB; }
{NUMBER} { strcpy(yylval.name, yytext); return (NUMBER); }
{IDENTIFIER} { strcpy(yylval.name, yytext); return (IDENTIFIER); }
{STRING} { strcpy(yylval.name, yytext); return (STRING); }
{COMMENT} {;}
%%

int lexInOpen(char* filename)
{
	tabs = 1;
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