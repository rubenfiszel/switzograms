const {
	CheckerPlugin
} = require('awesome-typescript-loader')


module.exports = {
	entry: './dist/map.js',
	output: {
		filename: 'bundle.js',
		path: 'dist/'
	},
	resolve: {
		extensions: ['', '.webpack.js', '.ts', '.js']
	},
	devtool: 'source-map',
	module: {
		loaders: [{
			test: /\.tsx?$/,
			loader: 'awesome-typescript-loader'
		}, {
			test: /\.json$/,
			loader: 'json'
		}]
	}
}

