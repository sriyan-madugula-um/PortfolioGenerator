from flask import Flask, request, jsonify, render_template
import os
from PyPDF2 import PdfFileReader
from jinja2 import Environment, FileSystemLoader

