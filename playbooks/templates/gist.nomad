job "{{ gist.split('/')[-1] }}" {

  type = "batch"
  datacenters = [ "dc1" ]

  group "default" {

    count = 1
    restart {
      attempts = 0
      mode = "fail"
    }
    task "gist-test" {
      driver = "docker"
      resources {
        memory = 512
      }
      config {
        image = "localhost:5000/gists"
        command = "python"
        args = [
          "/scripts/test_gist.py",
          "{{ gist }}",
          "{{ consul_client_address }}:8500"
        ]
      }
    }

  }

}
