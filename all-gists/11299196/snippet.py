require 'benchmark'
require 'json'
require 'msgpack'
require 'net/http'
require_relative './userland.pb'

def get(target)
  uri = URI(target)
  Net::HTTP.get(uri)
end

def test(runs, type, &block)
  GC.start
  uri = "#{@uri_s}.#{type}"
  v = 0
  a = 0
  cas = GC.stat
  res = get(uri)
  runs.times do
    v += res.bytes.count
    block.call(res)
  end
  cae = GC.stat
  a += cae[:total_allocated_object] - cas[:total_allocated_object]
  @vols[type] = v
  @objs[type] = a
end

@vols = {}
@objs = {}
@uri_s = "http://localhost:8080/users"
runs = 10000

puts "Running at #{runs} times"

Benchmark.bm(8) do |x|
  x.report('msgpack') do
    test(runs, :msgpack) do |res|
      data = MessagePack.unpack(res)
      raise unless data[0]['login'] == 'someguy'
    end
  end
  x.report('json') do
    test(runs, :json) do |res|
      data = JSON.parse(res)
      raise unless data[0]['login'] == 'someguy'
    end
  end
  x.report('protobuf') do
    @data = Userland::Users.new
    test(runs, :protobuf) do |res|
      @data.parse_from_string(res)
      raise unless @data.user.first.login == 'someguy'
    end
  end
end

@vols.each_pair do |k, v|
  puts "#{k.to_s.rjust(8, ' ')}: #{sprintf("%0.2f", v/1024.0/1024.0)} mb"
end
@objs.each_pair do |k, v|
  puts "#{k.to_s.rjust(8, ' ')}: #{v/1024}k allocs"
end