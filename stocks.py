from flask import Flask,render_template,request,redirect
import requests
import simplejson as json
import numpy as np
from pandas import *
import pandas
from datetime import date, timedelta
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.util.string import encode_utf8
#from bokeh.resources import INLINE

app = Flask(__name__)

app.vars={}


@app.route('/index',methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')
	else:
		app.vars['ticker'] = request.form['ticker']
	print(app.vars['ticker'])
	try:
		r = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/"+app.vars['ticker']+".json?auth_token=8XNJ9GnZjgoLQzcRH_87")
	except requests.exceptions.ConnectionError as e:
		print("Connection timed out. Try again")
		return redirect('/timeout')
	app.vars['D'] = json.loads(r.text)
	return redirect('/main')

@app.route('/main')
def main():
	if 'dataset' in app.vars['D']:
		print('valid')
		return redirect('/plot')
	print('invalid')
	return redirect('/error')

#####################################

@app.route('/plot')
def plot_display():
	today = date.today()
	if today.month == 1:
		new_month = 12
		new_year = today.year-1
	else:
		new_month = today.month-1
		new_year = today.year
	m_onemonth = today.replace(month=new_month, year = new_year)

	data = np.array(app.vars['D']['dataset']['data'])[:,1:].astype(float)
	dates = np.array(app.vars['D']['dataset']['data'])[:,0].astype('M8[D]')
	c_header = np.array(app.vars['D']['dataset']['column_names']).astype(str)

	S = Series(data.T.tolist(), index = c_header[1:]).to_dict()

	DF = DataFrame(S, index=dates).sort_index(ascending=False)

	x = DF[today:m_onemonth].index
	y = DF[today:m_onemonth]["Close"][::-1]

	p = figure(title=app.vars['ticker']+" closing price previous month", plot_height=300, plot_width = 600, x_axis_type="datetime")
	p.line(x,y,color = "#2222aa", line_width = 3)
	
	#js_res=INLINE.render_js()
	#css_res=INLINE.render_css()

	script, div = components(p)#, INLINE)
	print(div)
	
	return render_template('plot.html',ticker=app.vars['ticker'], div=div, script=script)#, js_resources=js_res, css_resources=css_res)
	#return encode_utf8(html)

@app.route('/error')
def error_display():
	return render_template('error.html', ticker=app.vars['ticker'])

@app.route('/timeout')
def TO_display():
	return render_template('timeout.html')

if __name__ == "__main__":
    app.run()
